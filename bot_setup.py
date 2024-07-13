import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!dbb ", intents=intents, help_command=None)

def get_bot():
    return bot

def get_subscribed_channels():
    if os.path.exists('subscribed_channels.json'):
        with open('subscribed_channels.json', 'r') as f:
            data = json.load(f)
            return data
    return {}

def save_subscribed_channels(subscribed_channels):
    with open('subscribed_channels.json', 'w') as f:
        json.dump(subscribed_channels, f, indent=4)
