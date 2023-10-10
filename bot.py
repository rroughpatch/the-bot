import asyncio
import discord
from discord.ext import commands
from utils import delete_message, get_timestamp

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild

    if before.channel != after.channel:
        if before.channel != after.channel:
            if after.channel and not member.bot:
                voice_channel = after.channel
                formatted_timestamp = get_timestamp()

                for channel in guild.voice_channels:
                    if channel == voice_channel:
                        text_channel = guild.get_channel(channel.id)

                        message = await text_channel.send(
                            f'{formatted_timestamp} **{member.display_name}** Connected!'
                        )

                        await delete_message(message, 20)

            elif before.channel and not member.bot:
                voice_channel = before.channel
                formatted_timestamp = get_timestamp()

                for channel in guild.voice_channels:
                    if channel == voice_channel:
                        text_channel = guild.get_channel(channel.id)

                        message = await text_channel.send(
                            f'{formatted_timestamp} **{member.display_name}** Disconnected!'
                        )

                        await delete_message(message, 20)


if __name__ == '__main__':
    bot.run(bot_token)
