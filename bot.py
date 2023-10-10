import asyncio
import discord
from discord.ext import commands
import utils as utils
import requests
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

song_queue = []
current_index = 0


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
                formatted_timestamp = utils.get_timestamp()
                for channel in guild.voice_channels:
                    if channel == voice_channel:
                        text_channel = guild.get_channel(channel.id)

                        message = await text_channel.send(
                            f'{formatted_timestamp} **{member.display_name}** Connected!'
                        )
                        await utils.delete_message(message, 20)

            elif before.channel and not member.bot:
                voice_channel = before.channel
                formatted_timestamp = utils.get_timestamp()
                for channel in guild.voice_channels:
                    if channel == voice_channel:
                        text_channel = guild.get_channel(channel.id)

                        message = await text_channel.send(
                            f'{formatted_timestamp} **{member.display_name}** Disconnected!'
                        )
                        await utils.delete_message(message, 20)


@bot.command()
async def play(ctx, *, track_name):
    """Add a track to the queue and play if it's the first track."""
    global current_index

    if not ctx.voice_client:
        await utils.connect_to_voice_channel(ctx)

    if utils.is_valid_url(track_name):
        file_path = await utils.download_audio_from_url(track_name)
    else:
        file_path = await utils.process_file_attachment(ctx, track_name)

    if file_path:
        song_queue.append(file_path)

        if not ctx.voice_client.is_playing():
            await play_next(ctx)

        utils.schedule_temp_file_cleanup(ctx, file_path)


async def play_next(ctx):
    """Play the next track in the queue if available."""
    global current_index

    if current_index < len(song_queue):
        track_name = song_queue[current_index]
        source = discord.FFmpegPCMAudio(executable="ffmpeg", source=track_name)

        ctx.voice_client.play(source, after=lambda e: play_next(ctx))
        current_index += 1

        metadata = utils.get_mp3_metadata(track_name)

        if metadata:
            embed = discord.Embed(title=f"[{metadata['title']}]({track_name})", color=discord.Color.green())
            embed.add_field(name="Artist", value=metadata.get("artist", "Unknown"))
            embed.add_field(name="Album", value=metadata.get("album", "Unknown"))

            await ctx.send(embed=embed, delete_after=20)
    else:
        await ctx.voice_client.disconnect()
        current_index = 0  # Reset the index


@bot.command()
async def skip(ctx):
    """Skip the currently playing track."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current track.")
    else:
        await ctx.send("I'm not playing anything right now.")


@bot.command()
async def queue(ctx):
    """List the tracks in the queue."""
    if queue:
        queue_list = '\n'.join(song_queue)
        await ctx.send(f"**Queue:**\n{queue_list}")
    else:
        await ctx.send("The queue is empty.")


@bot.command()
async def clear_queue(ctx):
    """Clear the queue of tracks."""
    global current_index, song_queue
    queue.clear()
    current_index = 0
    if ctx.voice_client:
        ctx.voice_client.stop()
    await ctx.send("The queue has been cleared.")


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await channel.connect()
        else:
            await ctx.send("I'm already in a voice channel.")
    else:
        await ctx.send("You need to be in a voice channel to use this command.")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel right now.")


if __name__ == '__main__':
    bot.run(bot_token)
