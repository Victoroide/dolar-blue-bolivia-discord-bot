import discord
from discord.ext import commands
from firebase_client import get_latest_usdt_to_bob

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

subscribed_channels = {}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready')
    from tasks import monitor_exchange_rate
    monitor_exchange_rate.start()

@bot.command(name='price')
async def fetch_price(ctx):
    price = get_latest_usdt_to_bob()
    if price:
        await ctx.send(f'El precio actual de USDT a BOB es: {price} BOB')
    else:
        await ctx.send('No se pudo obtener el precio actual.')

@bot.command(name='subscribe')
async def subscribe_channel(ctx):
    subscribed_channels[ctx.guild.id] = ctx.channel.id
    await ctx.send(f'Este canal ha sido suscrito para recibir actualizaciones diarias del precio de USDT a BOB.')

def get_bot():
    return bot

def get_subscribed_channels():
    return subscribed_channels
