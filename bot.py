# -*- coding: utf8 -*-
import nextcord
import requests
from datetime import datetime
from config import *
import os
import sqlite3
from nextcord.ext import tasks

from nextcord.ext import commands

intents = nextcord.Intents.all()



activity = None
status = None
if settings['status'] == "watching":
    activity = nextcord.Activity(type=nextcord.ActivityType.watching, name=settings['text'])
elif settings['status'] == "streaming":
    activity = nextcord.Streaming(name=settings['text'])
elif settings['status'] == "game":
    activity = nextcord.Game(name=settings['text'])
elif settings['status'] == "listening":
    activity = nextcord.Activity(type=nextcord.ActivityType.listening, name=settings['text'])
elif settings['status'] == "none":
    activity = None
else:
    activity = None
    print(__name__ + ' : Параметры конфигурации заданы неверно: ' + settings['status'])

if settings['activity'] == "offline":
    status = nextcord.Status.offline
elif settings['activity'] == "idle":
    status = nextcord.Status.idle
elif settings['activity'] == "dnd":
    status = nextcord.Status.dnd
elif settings['activity'] == "none":
    status = None
else:
    status = nextcord.Status.online
    print(__name__ + ' : Параметры конфигурации заданы неверно: ' + settings['activity'])

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents, activity= activity, status=status)

 

banner_db = sqlite3.connect('database/banner.db', timeout=10)
banner = banner_db.cursor()


            











for filename in os.listdir(".\cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


bot.run(settings['token'])