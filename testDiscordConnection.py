# bot.py
import os

import discord
from better_profanity import profanity
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!')



# Open badwords.txt file and read each line into an array
with open("censoredWords.txt") as file:
    censored_words = file.read().split()

# When a message is sent then bot will check it against the bad_words array 
# to see if there are any words in the message that are blacklisted
@bot.event
async def on_message(message):
    profanity.add_censor_words(censored_words)

    result = False;
    if profanity.contains_profanity(message.content.lower()):
        result = True
    if result:
        await message.delete()
        await message.channel.send("{}, your message has been deleted as it contains inappropriate text.".format(message.author.mention))
    
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

bot.run(TOKEN)