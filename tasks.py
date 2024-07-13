from discord.ext import tasks
from datetime import datetime, timedelta
import pytz
from firebase_client import get_latest_usdt_to_bob, get_historical_usdt_to_bob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import discord
from bot_setup import get_bot, get_subscribed_channels

bot = get_bot()
subscribed_channels = get_subscribed_channels()
default_timezone = 'America/La_Paz'

@tasks.loop(hours=24)
async def monitor_exchange_rate():
    print("Ejecutando tarea programada para monitorear el tipo de cambio.")
    tz = pytz.timezone(default_timezone)
    now = datetime.now(tz)
    target_time = now.replace(hour=14, minute=26, second=30, microsecond=0)  
    if now > target_time:
        target_time = target_time + timedelta(days=1)
    await discord.utils.sleep_until(target_time)

    print("Obteniendo precio actual...")
    price = get_latest_usdt_to_bob()
    if price:
        print(f"Precio obtenido: {price:.3f} BOB")
        historical_data = get_historical_usdt_to_bob(temporality='daily')
        timestamps = []
        prices = []
        for entry in historical_data:
            timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')).astimezone(tz)
            prices.append(entry['averagePrice'])
            timestamps.append(timestamp)

        fig, ax = plt.subplots()
        ax.plot(timestamps, prices, marker='o')
        ax.set(xlabel='Fecha', ylabel='Precio (BOB)', title='Historial por Día')
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate() 
        ax.grid()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)

        file = discord.File(buf, filename="historial.png")

        for guild_id, channel_id in subscribed_channels.items():
            channel = bot.get_channel(channel_id)
            if channel:
                print(f"Enviando mensaje a canal {channel.name} (ID: {channel_id}) en servidor {channel.guild.name} (ID: {guild_id})")
                await channel.send(
                    f"El precio actual de USDT a BOB es: {price:.3f} BOB",
                    file=file
                )
        buf.close() 
    else:
        print('No se pudo obtener el precio actual.')

@monitor_exchange_rate.before_loop
async def before_monitor_exchange_rate():
    await bot.wait_until_ready()
    print("Bot listo para monitorear el tipo de cambio.")
