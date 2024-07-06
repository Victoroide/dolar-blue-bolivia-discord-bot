import discord
from discord.ext import commands
from firebase_client import get_latest_usdt_to_bob
from bot_setup import get_bot, get_subscribed_channels

bot = get_bot()
subscribed_channels = get_subscribed_channels()

class SubscriptionView(discord.ui.View):
    def __init__(self, channels):
        super().__init__()
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in channels
        ]
        self.select = discord.ui.Select(
            placeholder="Selecciona un canal...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction):
        channel_id = int(self.select.values[0])
        subscribed_channels[interaction.guild.id] = channel_id
        await interaction.response.send_message(
            f"Canal {interaction.guild.get_channel(channel_id).mention} suscrito para recibir actualizaciones del precio del dólar.", 
            ephemeral=True
        )
        await interaction.message.delete()  # Elimina el mensaje de selección después de la selección

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready')
    from tasks import monitor_exchange_rate
    if not monitor_exchange_rate.is_running():
        monitor_exchange_rate.start()

@bot.command(name='precio')
async def fetch_price(ctx):
    price = get_latest_usdt_to_bob()
    if price:
        await ctx.send(f'El precio actual de USDT a BOB es: {price} BOB')
    else:
        await ctx.send('No se pudo obtener el precio actual.')

@bot.command(name='suscribir')
async def subscribe_channel(ctx):
    channels = [channel for channel in ctx.guild.text_channels]
    view = SubscriptionView(channels)
    await ctx.send("Selecciona el canal donde quieres recibir las actualizaciones del precio del dólar:", view=view)

@bot.command(name='desuscribir')
async def unsubscribe_channel(ctx):
    if ctx.guild.id in subscribed_channels and subscribed_channels[ctx.guild.id] == ctx.channel.id:
        del subscribed_channels[ctx.guild.id]
        await ctx.send(f"El canal {ctx.channel.mention} ha sido desuscrito de las actualizaciones del precio del dólar.")
    else:
        await ctx.send(f"El canal {ctx.channel.mention} no está suscrito a las actualizaciones del precio del dólar.")

@bot.command(name='help')
async def help_command(ctx):
    help_text = """
    **Comandos Disponibles:**
    `!dbb precio` - Muestra el precio actual de USDT a BOB.
    `!dbb suscribir` - Suscribe un canal para recibir actualizaciones diarias del precio del dólar.
    `!dbb desuscribir` - Desuscribe el canal actual de las actualizaciones del precio del dólar.
    """
    await ctx.send(help_text)
