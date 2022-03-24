#!/usr/bin/env python3
import asyncio
import discord
import json
import os
import datetime
from quart import Quart, request
from discord.ext import commands
# -*- coding: Unicode -*-

print('LibreNMS Discord notifier')
print('https://github.com/samicrusader/librenms-discord-notifier')

quart = Quart(__name__)


@quart.route('/send/<int:user_id>', methods=['POST'])
async def sendnotif(user_id):
    user = bot.get_user(int(user_id))
    channel = await user.create_dm()
    data = await request.data
    data = data.decode()
    data = json.loads(data, strict=False)
    msgdata = dict()
    msg = data['msg'].split('\n')
    for i in msg:
        try:
            i = i.split(': ')
            msgdata.update({i[0]: i[1]})
        except:
            pass
    if msgdata == dict():
        embed = discord.Embed(title='Test', description='Test message')
        await channel.send(embed=embed)
        return 'Done'
    if msgdata['Severity'] == 'critical':
        color = discord.Colour.red()
    elif msgdata['Severity'] == 'warning':
        color = discord.Colour.yellow()
    else:
        color = discord.Colour.default()
    embed = discord.Embed(author=data['hostname'], color=color, title=data['title'], description=data['msg'], timestamp=datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'))
    embed.add_field(name='System name', value=data['sysName'])
    embed.add_field(name='Rule name', value=msgdata['Rule'].replace('  ', ''))
    await channel.send(embed=embed)
    return 'Done'

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='nms!', intents=intents)


@bot.event
async def on_ready():
    print('Logged in as {0} <@!{1}>'.format(bot.user.name, str(bot.user.id)))
    await bot.change_presence(status=discord.Status.online)

# @bot.event
# async def on_command_error(ctx, error):
#    em = embedgen.error(error, bot)
#    await ctx.send('Something happened.', embed=em)


@bot.command()
async def timer(ctx, time: int):
    """async timer test"""
    await ctx.send('waiting')
    for x in range(0, time):
        await asyncio.sleep(1)
# </Bot>

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bp = loop.create_task(bot.start(os.environ['TOKEN']))
    wp = loop.create_task(
        quart.run(host='0.0.0.0', port=5003, loop=loop, use_reloader=False))
    gathered = asyncio.gather(bp, wp, loop=loop)
    try:
        loop.run_until_complete(gathered)
    except KeyboardInterrupt as e:
        loop.run_until_complete(bot.close())
