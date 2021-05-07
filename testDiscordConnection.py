# bot.py
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from dotenv import load_dotenv
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
testing_channel_id = 837522915410968609
welcome_channel_id = 819751860398456874
guild_id = 819751859945996300

scheduler = AsyncIOScheduler()
guild = None;
welcome_channel = None;
reminder_channel = None;

def in_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)

async def func():
    await bot.wait_until_ready()
    reminder_channel = bot.get_channel(testing_channel_id)
    await reminder_channel.send("Assignment Reminder")


@bot.command()
async def assignment_reminder(ctx, date, hour, minute):
    addScheduleByDateHourMinute(date, hour, minute)
    reminder_channel = bot.get_channel(testing_channel_id)
    print(testing_channel_id)
    await reminder_channel.send("Reminder added")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Ready")
    # Initializing scheduler
    scheduler.start()


@bot.event
async def on_member_join(member):
    guild = bot.get_guild(guild_id)
    welcome_channel = guild.get_channel(welcome_channel_id)
    await welcome_channel.send(f'Welcome to the {member.guild}, {member.mention}! :partying_face:')


def addScheduleByDateHourMinute(date, hour, minute):
    scheduler.add_job(func, CronTrigger(hour= hour, day= date, minute= minute))

bot.run(TOKEN)
