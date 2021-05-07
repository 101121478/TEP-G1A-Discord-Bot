
# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def ban(ctx,member):
    await bot.ban(member, reason=None)
    await ctx.channel.send("{} has been banned from the server".format(member))

@bot.command()
async def kick(ctx,member):
    await bot.kick(member, reason=None)
    await ctx.channel.send("{} has been kicked from the server".format(member))
    

   

bot.run(TOKEN)