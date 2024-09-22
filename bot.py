import os
import yt_dlp  # Replaced youtube_dl with yt_dlp
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types import AudioPiped

# Bot settings
API_ID = os.getenv("API_ID")  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API hash
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Bot token for controlling commands
SESSION_STRING = os.getenv("SESSION_STRING")  # String session of the second ID

# Chat ID where music will be played (your group ID)
CHAT_ID = -1002386315601  # Manually provided chat ID

# Create Pyrogram client
app = Client(
    session_name=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# PyTgCalls instance to handle voice chats
pytgcalls = PyTgCalls(app)

# YouTube download options, including cookies for authenticated requests
ydl_opts = {
    'format': 'bestaudio',
    'noplaylist': 'True',
    'cookiefile': 'cookies.txt',  # Use cookies for YouTube authentication
}

async def download_audio(url: str):
    """Download audio from YouTube"""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        audio_url = info_dict['url']
    return audio_url

@app.on_message(filters.command("play"))
async def play_music(client, message: Message):
    """Play music in the voice chat"""
    url = message.text.split(" ", 1)[1]

    # Download YouTube audio stream
    audio_url = await download_audio(url)

    # Send audio stream to PyTgCalls to play in voice chat
    await pytgcalls.join_group_call(
        CHAT_ID,
        AudioPiped(audio_url),
        stream_type=StreamType().local_stream
    )

    await message.reply_text("Playing audio in voice chat!")

@app.on_message(filters.command("stop"))
async def stop_music(client, message: Message):
    """Stop music in the voice chat"""
    await pytgcalls.leave_group_call(CHAT_ID)
    await message.reply_text("Stopped audio in voice chat!")

@app.on_message(filters.command("pause"))
async def pause_music(client, message: Message):
    """Pause music in the voice chat"""
    await pytgcalls.pause_stream(CHAT_ID)
    await message.reply_text("Paused audio in voice chat!")

@app.on_message(filters.command("resume"))
async def resume_music(client, message: Message):
    """Resume music in the voice chat"""
    await pytgcalls.resume_stream(CHAT_ID)
    await message.reply_text("Resumed audio in voice chat!")

# Start the bot and PyTgCalls
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Music bot is online!")

pytgcalls.start()
app.run()
