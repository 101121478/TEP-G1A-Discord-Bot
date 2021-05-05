# bot.py
import os
import mysql.connector

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

dbHost = os.getenv('dbHost')
dbUser = os.getenv('dbUser')
dbPassword = os.getenv('dbPassword')
db = os.getenv('database')

client = discord.Client()
bot = commands.Bot(command_prefix='!')

# Initialise connection to SQL database with details from .env file
mydb = mysql.connector.connect(
    host=dbHost,
    user=dbUser,
    password=dbPassword,
    database=db
)
mycursor = mydb.cursor()

def create_topics_table():
    mycursor.execute("CREATE TABLE topics (topic VARCHAR(30), count INT DEFAULT 0)")
    mydb.commit()

def does_topics_exists():
    mycursor.execute("SHOW TABLES LIKE 'topics'")
    result = mycursor.fetchone()
    if result:
        return True
    else:
        return False

if not does_topics_exists():
    print("Table does not exist")
    create_topics_table()

# Open badwords.txt file and read each line into an array
with open("badwords.txt") as file:
    bad_words = file.read().split()

# When a message is sent then bot will check it against the bad_words array 
# to see if there are any words in the message that are blacklisted
async def filter_messages(message):
    result = False;
    for bad_word in bad_words:
        if bad_word in message.content.lower():
            result = True
    if result:
        await message.delete()
        await message.channel.send("{}, your message has been censored.".format(message.author.mention))
    
    await bot.process_commands(message)

# Retreives all topics from the topics table and checks if any of them
# are in the message, if so then update the count for that topic by 1
def check_for_common_topic(message):
    mycursor.execute("SELECT * FROM topics")
    result = mycursor.fetchall()
    count = 0

    for topic in result:
        if topic[0] in message.content.lower() and message.author != bot.user and "!add_topic" not in message.content.lower():
            count = topic[1] + 1
            sql = "UPDATE topics SET count = {} WHERE topic = '{}'".format(count, topic[0])
            mycursor.execute(sql)
    
    mydb.commit()



@bot.event
async def on_message(message):
    await filter_messages(message)
    check_for_common_topic(message)


# Will retrieve the concepts/topics and the number of times they have been mentioned in the server
@bot.command()
async def get_common_topics(ctx):
    topics = []

    mycursor.execute("SELECT * FROM topics")
    result = mycursor.fetchall()

    if result:
        for topic in result:
            topics.append(str(topic))
        
        message = '\n'.join(topics)
        await ctx.channel.send(message)
    else:
        await ctx.channel.send("No topics in the table to display. Add a topic using the command !add_topic topic")

# Will add the new topic that the user enters when this command is entered e.g. !add_new_topic Python will add Python
@bot.command()
async def add_topic(ctx, topic):
    topic = topic.lower()
    sql = "SELECT * FROM topics WHERE topic = '{}'".format(topic)

    mycursor.execute(sql)
    result = mycursor.fetchall()

    if result:
        await ctx.channel.send("Topic: {} already exists in 'topics' table in database: {}.".format(topic, db))
    else:
        sql = "INSERT INTO topics (topic, count) VALUES (%s, %s)"
        val = (topic, 0)
        
        mycursor.execute(sql, val)
        mydb.commit()

        await ctx.channel.send("Added topic: {} to the 'topics' table in database: {}.".format(topic, db))

# Deletes the topic entered by the user from the database
@bot.command()
async def delete_topic(ctx, topic):
    topic = topic.lower()
    sql = "SELECT * FROM topics WHERE topic = '{}'".format(topic)

    mycursor.execute(sql)
    result = mycursor.fetchall()

    if not result:
        await ctx.channel.send("No topic: {} in 'topics' table in database: {}.".format(topic, db))
    else:
        sql = "DELETE FROM topics WHERE topic = '{}'".format(topic)

        mycursor.execute(sql)
        mydb.commit()

        await ctx.channel.send("Topic: {} has been deleted from 'topics' table in database: {}.".format(topic, db))

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

bot.run(TOKEN)