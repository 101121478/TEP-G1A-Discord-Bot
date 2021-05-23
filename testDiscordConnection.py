
# bot.py
import os
import discord
from discord.ext.commands.core import has_permissions
from discord.ext.commands.errors import CommandNotFound
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np

from better_profanity import profanity
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import commands
from numpy import isposinf

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!')

# Open badwords.txt file and read each line into an array
with open("censoredWords.txt") as file:
    censored_words = file.read().split()

# Get SQL database details
dbHost = os.getenv('dbHost')
dbUser = os.getenv('dbUser')
dbPassword = os.getenv('dbPassword')
db = os.getenv('database')

# Initialise connection to SQL database with details from .env file
def databaseConnection():
    mydb = mysql.connector.connect(
        host=dbHost,
        user=dbUser,
        password=dbPassword,
        database=db
    )
    return mydb

# Creates a topics database table
def create_topics_table():
    mydb = databaseConnection()
    mydb.cursor().execute("CREATE TABLE topics (topic VARCHAR(30), count INT DEFAULT 0)")
    mydb.commit()
    mydb.close()

# Creates a strikes database table
def create_strikes_table():
    mydb = databaseConnection()
    mydb.cursor().execute("CREATE TABLE strikes (user VARCHAR(30), count INT DEFAULT 0)")
    mydb.commit()
    mydb.close()

# Checks if the topics table exists in database
def does_topics_exists():
    mydb = databaseConnection()
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES LIKE 'topics'")
    result = mycursor.fetchone()
    if result:
        return True
    else:
        return False

# Checks if the strikes table exists in database
def does_strikes_exists():
    mydb = databaseConnection()
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES LIKE 'strikes'")
    result = mycursor.fetchone()
    if result:
        return True
    else:
        return False

# Check if topics and strikes table exist in database. If not create them.
if not does_topics_exists():
    print("Topics table does not exist")
    create_topics_table()
if not does_strikes_exists():
    print("Strikes table does not exist")
    create_strikes_table()

# Simple check if the current channe is the admin-room channel
# Used by topic/concept commands and message filtering to determine if function should run
def in_adminChannel(channel_id):
    channel = bot.get_channel(845131902424055819)

    if channel_id == channel.id:
        return True
    else:
        return False


# Retreives all topics from the topics table and checks if any of them
# are in the message, if so then update the count for that topic by 1
def check_message_for_topic(message):
    if not in_adminChannel(message.channel.id):
        mydb = databaseConnection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM topics")
        result = mycursor.fetchall()
        count = 0

        for topic in result:
            if topic[0] in message.content.lower() and message.author != bot.user and "!add_topic" not in message.content.lower():
                count = topic[1] + 1
                sql = "UPDATE topics SET count = {} WHERE topic = '{}'".format(count, topic[0])
                mycursor.execute(sql)
        
        mydb.commit()
        mydb.close()
    
# When a message is sent the bot will check it against the bad_words array 
# to see if there are any words in the message that are blacklisted
# If so then delete the message and add a strike to the strikes database table for the user
async def filter_message(message):
    mydb = databaseConnection()
    mycursor = mydb.cursor()
    profanity.add_censor_words(censored_words)
    
    containsProfanity = False
    if profanity.contains_profanity(message.content.lower()):
        containsProfanity = True

    if containsProfanity:
        mycursor.execute("SELECT * FROM strikes WHERE user='{}'".format(message.author.name))
        result = mycursor.fetchall()
        count = 1

        if result:
            print('User: {} is in strikes table'.format(message.author.name))
            for row in result:
                count = row[1] + 1
                sql = "UPDATE strikes SET count = {} WHERE user = '{}'".format(count, row[0])
                mycursor.execute(sql)
        else:
            print("User:  {} not in strikes table".format(message.author.name))
            sql = "INSERT INTO strikes (user, count) VALUES (%s, %s)"
            val = (message.author.name, count)
            mycursor.execute(sql, val)
        
        mydb.commit()
        mydb.close()

        await message.delete()
        await message.channel.send("{}, your message has been deleted as it contains inappropriate text. And you have received a strike. Total Strikes: {}".format(message.author.mention, count))


# Plots a bar graph of the x and y values enetered
# also takes in an xlabel, ylabel, title and filename
# bar graph is sent to the discord channel as an image where it can be viewed and/or saved.
async def plot_graph(ctx, x, y, xlabel, ylabel, title, filename):
    plt.clf()
    plt.bar(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.yticks(np.arange(min(y), max(y)+1, 1))
    plt.title(title)
    plt.savefig(fname=filename)
    await ctx.channel.send(file=discord.File('{}.png'.format(filename)))
    os.remove('{}.png'.format(filename))



# Will retrieve the concepts/topics and the number of times they have been mentioned in the server
@bot.command()
#@has_permissions(administrator=True)
async def display_strikes(ctx):
    if in_adminChannel(ctx.channel.id):
        users = []
        strikes = []
        mydb = databaseConnection()
        mycursor = mydb.cursor()


        mycursor.execute("SELECT * FROM strikes")
        result = mycursor.fetchall()

        if result:
            for result in result:       # for each tuple in result store the topic and its count in seperate arrays
                users.append(result[0])
                strikes.append(result[1])

            await plot_graph(ctx, users, strikes, 'Member', 'Strikes', 'Members and the number of strikes they have', 'common_topics')

        else:
            await ctx.channel.send("No members in the table to display.")

        mydb.close()


# Will retrieve the concepts/topics and the number of times they have been mentioned in the server
@bot.command()
#@has_permissions(administrator=True)
async def display_topics(ctx):
    if in_adminChannel(ctx.channel.id):
        topics = []
        counts = []
        mostCommonTopic = ""
        commonTopicCount = 0

        mydb = databaseConnection()
        mycursor = mydb.cursor()


        mycursor.execute("SELECT * FROM topics")
        result = mycursor.fetchall()

        if result:
            for result in result:       # for each tuple in result store the topic and its count in seperate arrays
                topics.append(result[0])
                counts.append(result[1])

                if result[1] > commonTopicCount:    # Find the most mentioned topic. Checks if next topic has a higher count then current highest count.
                    commonTopicCount = result[1]
                    mostCommonTopic = result[0]

            await ctx.channel.send("Currently the most commonly discussed topic/concept is {}. It has been mentioned {} times.".format(mostCommonTopic, commonTopicCount))
            await plot_graph(ctx, topics, counts, 'Topic/Concept', 'Count', 'Number of times Topics/Concepts have been discussed', 'common_topics')

        else:
            await ctx.channel.send("No topics in the table to display. Add a topic using the command !add_topic topic")

        mydb.close()

# Will add the new topic that the user enters when this command is entered e.g. !add_new_topic Python will add Python
@bot.command()
async def add_topic(ctx, topic):
    if in_adminChannel(ctx.channel.id):
        mydb = databaseConnection()
        mycursor = mydb.cursor()

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
        
        mydb.close()

# Deletes the topic entered by the user from the database
@bot.command()
async def delete_topic(ctx, topic):
    if in_adminChannel(ctx.channel.id):
        mydb = databaseConnection()
        mycursor = mydb.cursor()

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

        mydb.close()
        
@bot.command(pass_context = True)
@has_permissions(ban_members=True)
async def ban(ctx, user: discord.User):
    mydb = databaseConnection()
    mycursor = mydb.cursor()

    sql = "SELECT * FROM strikes WHERE user = '{}'".format(user.name)

    mycursor.execute(sql)
    result = mycursor.fetchall()

    if result:      # If user exists in strikes table then remove them from the table when they are banned
        sql = "DELETE FROM strikes WHERE user = '{}'".format(user.name)

        mycursor.execute(sql)
        mydb.commit()
    
    mydb.close()

    await ctx.guild.ban(user)
    await ctx.channel.send("{} has been banned from the server".format(user))
    

@bot.command(pass_context = True)
@has_permissions(kick_members=True)
async def kick(ctx, user: discord.User):
    mydb = databaseConnection()
    mycursor = mydb.cursor()

    sql = "SELECT * FROM strikes WHERE user = '{}'".format(user.name)

    mycursor.execute(sql)
    result = mycursor.fetchall()

    if result:      # If user exists in strikes table then remove them from the table when they are kicked
        sql = "DELETE FROM strikes WHERE user = '{}'".format(user.name)

        mycursor.execute(sql)
        mydb.commit()
    
    mydb.close()

    await ctx.guild.kick(user)
    await ctx.channel.send("{} has been kicked from the server".format(user))

# Whenever a message is sent call filter_messages to check the messages and censor any inappropriate ones.
# Also call check_message_for_topic() to check the message and identify if any topics from the topics table are mentioned if so then count it.
@bot.event
async def on_message(message):
    await filter_message(message)
    check_message_for_topic(message)

    await bot.process_commands(message)

# If the user enters a command that does not exist or enters a command wrong then the bot 
# will send a message to inform the user that the command isn't recognised.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return await ctx.channel.send(error)
    raise error

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


bot.run(TOKEN)