import discord
from discord.ext import commands
from discord import app_commands
from firebase_client import get_latest_usdt_to_bob, get_historical_usdt_to_bob
from bot_setup import get_bot, get_subscribed_channels, save_subscribed_channels
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

bot = get_bot()
subscribed_channels = get_subscribed_channels()
user_timezones = {} 
default_timezone = 'America/La_Paz'

common_timezones = [
    'UTC', 'US/Pacific', 'US/Eastern', 'Europe/London', 'Europe/Berlin',
    'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Kolkata', 'Australia/Sydney', 
    'America/Los_Angeles', 'America/New_York', 'America/Sao_Paulo', 
    'America/Argentina/Buenos_Aires', 'America/Mexico_City', 'America/Bogota', 
    'America/Lima', 'America/La_Paz'
]

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
        save_subscribed_channels(subscribed_channels)
        await interaction.response.send_message(
            f"Canal {interaction.guild.get_channel(channel_id).mention} suscrito para recibir actualizaciones del precio del dólar.", 
            ephemeral=True
        )
        await interaction.message.delete() 

class TimezoneSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        options = [discord.SelectOption(label=tz, value=tz) for tz in common_timezones]
        self.select = discord.ui.Select(
            placeholder="Selecciona tu zona horaria...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction):
        timezone = self.select.values[0]
        user_timezones[interaction.user.id] = timezone
        await interaction.response.send_message(
            f"Tu zona horaria se ha establecido a {timezone}.",
            ephemeral=True
        )
        await interaction.message.delete()

class HistoricalView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HistoricalButton(label='Por Hora', custom_id='hourly'))
        self.add_item(HistoricalButton(label='Por Día', custom_id='daily'))

class HistoricalButton(discord.ui.Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary if custom_id == 'hourly' else discord.ButtonStyle.secondary, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        temporality = self.custom_id
        historical_data = get_historical_usdt_to_bob(temporality=temporality)
        user_timezone = user_timezones.get(interaction.user.id, default_timezone)
        await self.display_historical_data(interaction, historical_data, temporality, user_timezone)
        await interaction.message.delete()  

    async def display_historical_data(self, interaction, data, temporality, timezone):
        tz = pytz.timezone(timezone)
        timestamps = []
        prices = []

        for entry in data:
            timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')).astimezone(tz)
            price = entry['averagePrice']
            timestamps.append(timestamp)
            prices.append(price)

        fig, ax = plt.subplots()
        ax.plot(timestamps, prices, marker='o')

        ax.set(xlabel='Hora' if temporality == 'hourly' else 'Fecha', ylabel='Precio (BOB)', title=f'Historial por {"Hora" if temporality == "hourly" else "Día"}')

        if temporality == 'hourly':
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=tz))
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d', tz=tz))
        fig.autofmt_xdate() 

        ax.grid()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)

        file = discord.File(buf, filename="historial.png")
        
        message = f"**Historial por {'Hora' if temporality == 'hourly' else 'Día'}**\n\n"
        for entry in data:
            timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')).astimezone(tz)
            if temporality == 'hourly':
                timestamp_str = timestamp.strftime('%H:%M')
                message += f"Hora: {timestamp_str} - Precio: {entry['averagePrice']:.3f} BOB\n"
            else:
                timestamp_str = timestamp.strftime('%d %b')
                message += f"Fecha: {timestamp_str} - Precio: {entry['averagePrice']:.3f} BOB\n"

        await interaction.channel.send(message, file=file) 

@bot.command(name='set_timezone')
async def set_timezone(ctx):
    view = TimezoneSelectView()
    await ctx.send("Selecciona tu zona horaria:", view=view)

@bot.command(name='precio')
async def fetch_price(ctx):
    price = get_latest_usdt_to_bob()
    if price:
        await ctx.send(f'El precio actual de USDT a BOB es: {price:.3f} BOB')
    else:
        await ctx.send('No se pudo obtener el precio actual.')

@bot.command(name='suscribir')
async def subscribe_channel(ctx):
    if ctx.guild.id in subscribed_channels:
        channel_id = subscribed_channels[ctx.guild.id]
        existing_channel = ctx.guild.get_channel(channel_id)
        if existing_channel:
            await ctx.send(f"El canal {existing_channel.mention} ya está suscrito para recibir actualizaciones del precio del dólar.")
            return

    channels = [channel for channel in ctx.guild.text_channels]
    view = SubscriptionView(channels)
    await ctx.send("Selecciona el canal donde quieres recibir las actualizaciones del precio del dólar:", view=view)

@bot.command(name='desuscribir')
async def unsubscribe_channel(ctx):
    if ctx.guild.id in subscribed_channels and subscribed_channels[ctx.guild.id] == ctx.channel.id:
        del subscribed_channels[ctx.guild.id]
        save_subscribed_channels(subscribed_channels) 
        await ctx.send(f"El canal {ctx.channel.mention} ha sido desuscrito de las actualizaciones del precio del dólar.")
    else:
        await ctx.send(f"El canal {ctx.channel.mention} no está suscrito a las actualizaciones del precio del dólar.")


@bot.command(name='historial')
async def historial_command(ctx):
    view = HistoricalView()
    await ctx.send("Selecciona la temporalidad del historial:", view=view)

@bot.command(name='help')
async def help_command(ctx):
    help_text = """
    **Comandos Disponibles:**
    `/dbb precio` - Muestra el precio actual de USDT a BOB.
    `/dbb suscribir` - Suscribe un canal para recibir actualizaciones diarias del precio del dólar.
    `/dbb desuscribir` - Desuscribe el canal actual de las actualizaciones del precio del dólar.
    `/dbb historial` - Muestra el historial de cambios del tipo de cambio del dólar. Puedes seleccionar entre ver por hora o por día.
    `/dbb set_timezone` - Establece tu zona horaria para mostrar los tiempos correctamente mediante una lista desplegable.
    """
    await ctx.send(help_text)
