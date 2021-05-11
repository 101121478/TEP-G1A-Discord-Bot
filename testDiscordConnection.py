# bot.py
import os
import discord
import mysql.connector
import matplotlib.pyplot as plt

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

# Get SQL database details
dbHost = os.getenv('dbHost')
dbUser = os.getenv('dbUser')
dbPassword = os.getenv('dbPassword')
db = os.getenv('database')

# Initialise connection to SQL database with details from .env file
mydb = mysql.connector.connect(
    host=dbHost,
    user=dbUser,
    password=dbPassword,
    database=db
)
mycursor = mydb.cursor()

# Creates a topics database table
def create_topics_table():
    mycursor.execute("CREATE TABLE topics (topic VARCHAR(30), count INT DEFAULT 0)")
    mydb.commit()

# Checks if the topics table exists in database
def does_topics_exists():
    mycursor.execute("SHOW TABLES LIKE 'topics'")
    result = mycursor.fetchone()
    if result:
        return True
    else:
        return False

# Check if topics table exists in database. If not then call create_topics_table() to create the table.
if not does_topics_exists():
    print("Table does not exist")
    create_topics_table()

# Plots a bar graph of the topics/concepts and their counts
# bar graph is sent to the discord channel as an image where it can be viewed and/or saved.
async def plot_graph(ctx, topics, counts):
    plt.clf()
    plt.bar(topics, counts)
    plt.xlabel('Topic/Concept')
    plt.ylabel('Count')
    plt.title('Number of times Topics/Concepts have been discussed')
    plt.savefig(fname='common_topics')
    await ctx.channel.send(file=discord.File('common_topics.png'))
    os.remove('common_topics.png')


# Retreives all topics from the topics table and checks if any of them
# are in the message, if so then update the count for that topic by 1
def check_message_for_topic(message):
    mycursor.execute("SELECT * FROM topics")
    result = mycursor.fetchall()
    count = 0

    for topic in result:
        if topic[0] in message.content.lower() and message.author != bot.user and "!add_topic" not in message.content.lower():
            count = topic[1] + 1
            sql = "UPDATE topics SET count = {} WHERE topic = '{}'".format(count, topic[0])
            mycursor.execute(sql)
    
    mydb.commit()
    
# When a message is sent then bot will check it against the bad_words array 
# to see if there are any words in the message that are blacklisted
async def filter_message(message):
    profanity.add_censor_words(censored_words)
    
    result = False
    if profanity.contains_profanity(message.content.lower()):
        result = True
    if result:
        await message.delete()
        await message.channel.send("{}, your message has been deleted as it contains inappropriate text.".format(message.author.mention))

        
# Whenever a message is sent call filter_messages to check the messages and censor any inappropriate ones.
# Also call check_message_for_topic() to check the message and identify if any topics from the topics table are mentioned if so then count it.
@bot.event
async def on_message(message):
    await filter_message(message)
    check_message_for_topic(message)
    await bot.process_commands(message)

# Will retrieve the concepts/topics and the number of times they have been mentioned in the server
@bot.command()
async def display_topics(ctx):
    topics = []
    counts = []
    mostCommonTopic = ""
    commonTopicCount = 0


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
        await plot_graph(ctx, topics, counts)

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