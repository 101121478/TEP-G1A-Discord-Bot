# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!')


# Open badwords.txt file and read each line into an array
with open("badwords.txt") as file:
    bad_words = file.read().split()

# When a message is sent then bot will check it against the bad_words array 
# to see if there are any words in the message that are blacklisted
@bot.event
async def on_message(message):
    result = False;
    for bad_word in bad_words:
        if bad_word in message.content.lower():
            result = True
    if result:
        await message.delete()
        await message.channel.send("{}, your message has been censored.".format(message.author.mention))
    
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

bot.run(TOKEN)