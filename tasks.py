import datetime
import asyncio
from discord.ext import tasks
from firebase_client import get_latest_usdt_to_bob
from commands import get_bot, get_subscribed_channels

bot = get_bot()

@tasks.loop(hours=24)
async def monitor_exchange_rate():
    current_price = get_latest_usdt_to_bob()
    if current_price:
        subscribed_channels = get_subscribed_channels()
        for guild_id, channel_id in subscribed_channels.items():
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f'El precio actual de USDT a BOB es: {current_price} BOB')

@monitor_exchange_rate.before_loop
async def before():
    await bot.wait_until_ready()
    now = datetime.datetime.now(datetime.timezone.utc)
    target_time = datetime.datetime.combine(now.date(), datetime.time(hour=13, minute=0, second=0, tzinfo=datetime.timezone.utc))
    if now > target_time:
        target_time = target_time + datetime.timedelta(days=1)
    await asyncio.sleep((target_time - now).total_seconds())

monitor_exchange_rate.start()
