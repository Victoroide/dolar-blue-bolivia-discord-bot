from config import DISCORD_TOKEN
from commands import get_bot

bot = get_bot()
bot.run(DISCORD_TOKEN)
