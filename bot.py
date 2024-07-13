import config, commands
from bot_setup import get_bot
from tasks import monitor_exchange_rate

bot = get_bot()

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    monitor_exchange_rate.start()

if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)
