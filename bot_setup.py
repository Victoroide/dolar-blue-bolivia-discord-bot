import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!dbb ", intents=intents, help_command=None)

subscribed_channels = {}

def get_bot():
    return bot

def get_subscribed_channels():
    return subscribed_channels
