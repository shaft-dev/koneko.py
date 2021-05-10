import discord
import os
from discord.ext import commands

os.chdir("Koneko") # for when my working directory contains koneko folder

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="nyaa!", intents = intents)
client = discord.Client()

for file in os.listdir("./Cogs"):
    if file.find(".py") != -1:
        file = file.replace(".py", "")
        bot.load_extension("Cogs." + file)
    
bot.run(open("botkey.txt").read())
