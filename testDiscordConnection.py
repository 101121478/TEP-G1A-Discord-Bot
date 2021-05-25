# bot.py
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from dotenv import load_dotenv
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents().all())

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
testing_channel_id = 837522915410968609
welcome_channel_id = 819751860398456874
guild_id = 819751859945996300

#AsyncScheduler
scheduler = AsyncIOScheduler()
guild = None;
welcome_channel = None;
reminder_channel = None;

def in_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)


def in_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)


#part of the assingment_reminder command
def addScheduleByDateHourMinute(desc, date, hour, minute):
    scheduler.add_job(send_reminder, CronTrigger(hour= hour, day= date, minute= minute), [desc])








#Sending the reminder
async def send_reminder(reminderDesc):
    await bot.wait_until_ready()
    reminder_channel = bot.get_channel(837522915410968609)
    await reminder_channel.send(reminderDesc)

async def func():
    await bot.wait_until_ready()
    reminder_channel = bot.get_channel(testing_channel_id)
    await reminder_channel.send("Assignment Reminder")











#Reminder function
@bot.command()
async def reminder(ctx, desc, date, hour, minute):
    addScheduleByDateHourMinute(desc, date, hour, minute)
    reminder_channel = bot.get_channel(837522915410968609)
    await reminder_channel.send(desc + " reminder added")







#Send welcome notification to the new member
@bot.event
async def on_member_join(member):
    guild = bot.get_guild(guild_id)
    welcome_channel = guild.get_channel(welcome_channel_id)
    await welcome_channel.send(f'Welcome to the {member.guild}, {member.mention}! :partying_face:')


#Send notification when somebody left the server
@bot.event
async def on_member_remove(member):
    guild = bot.get_guild(819751859945996300)
    welcome_channel = guild.get_channel(819751860398456874)
    await welcome_channel.send(f'{member.mention} has left the server')


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Ready")
    # Initializing scheduler
    scheduler.start()


bot.run(TOKEN)
