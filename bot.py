from config import DISCORD_TOKEN
from commands import get_bot

bot = get_bot()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
