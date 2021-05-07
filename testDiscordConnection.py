
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

@bot.command(pass_context = True)
async def ban(ctx, user: discord.User):
   await ctx.guild.ban(user)
   await ctx.channel.send("{} has been banned from the server".format(user))
    

@bot.command(pass_context = True)
async def kick(ctx, user: discord.User):
    await ctx.guild.kick(user)
    await ctx.channel.send("{} has been kicked from the server".format(user))




bot.run(TOKEN)