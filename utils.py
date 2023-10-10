import asyncio
from datetime import datetime
import eyed3
import os
import discord
from urllib.parse import urlparse, urlunparse
import requests


def format_metadata(metadata, track_name):
    formatted_metadata = f"**Now playing:** {metadata['title']} "
    formatted_metadata += f"by {metadata['artist']}\n"
    formatted_metadata += f"**Album:** {metadata['album']}\n"

    return formatted_metadata


def get_mp3_metadata(file_path):
    audiofile = eyed3.load(file_path)

    if audiofile.tag:
        title = audiofile.tag.title
        artist = audiofile.tag.artist
        album = audiofile.tag.album
        track_number = audiofile.tag.track_num[0]

        return {
            'title': title,
            'artist': artist,
            'album': album,
            'track_number': track_number,
        }
    return None


def schedule_temp_file_cleanup(ctx, file_path):
    def cleanup_temp_file():
        if os.path.exists(file_path):
            os.remove(file_path)

    ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
    ctx.voice_client.source.volume = 0.6
    ctx.voice_client.source.after = cleanup_temp_file


async def delete_message(message, delay):
    await asyncio.sleep(delay)
    await message.delete()


def get_timestamp():
    timestamp = int(datetime.now().timestamp())
    return f'<t:{timestamp}:R>'


async def connect_to_voice_channel(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel to use this command.")


def is_valid_url(url):
    return url.startswith("http")


async def download_audio_from_url(url):
    url_parts = urlparse(url)
    file_name = os.path.basename(url_parts.path)
    simplified_file_name = ''.join(e for e in file_name if e.isalnum() or e.isspace())
    file_path = f"temp/{simplified_file_name}"

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    return None


async def process_file_attachment(ctx, file_name):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please provide an audio file attachment.")
        return None

    attachment = ctx.message.attachments[0]

    allowed_extensions = ['.mp3', '.wav', '.ogg']
    if not any(attachment.filename.endswith(ext) for ext in allowed_extensions):
        await ctx.send("Unsupported file format. Please provide an audio file (e.g., .mp3).")
        return None

    file_path = f"temp/{attachment.filename}"
    await attachment.save(file_path)

    return file_path


def clean_audio_url(audio_url):
    parsed_url = urlparse(audio_url)
    clean_url = urlunparse(parsed_url._replace(query=''))
    return clean_url