import discord
from discord.ext import commands
import speech_recognition as sr
import sqlite3
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_PATH = "C:/ffmpeg/bin/ffmpeg.exe"

# Database setup
DB_FILE = "voice_logs.db"

def init_db():
    """Initialize the database to store voice messages."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS voice_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    conn.close()

init_db()

@bot.command()
async def joinyo(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("I'm now in the voice channel and listening!")
    else:
        await ctx.send("You need to be in a voice channel!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def listen(ctx):
    if not ctx.voice_client:
        await ctx.send("Bot is not in a voice channel. Use `!joinyo` first.")
        return

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        await ctx.send("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
            text = recognizer.recognize_google(audio)

            # Store in database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO voice_messages (user, text) VALUES (?, ?)", (str(ctx.author), text))
            conn.commit()
            conn.close()

            await ctx.send(f"Stored: {text}")

        except sr.UnknownValueError:
            await ctx.send("Sorry, I couldn't understand what you said.")
        except sr.RequestError:
            await ctx.send("Could not request results from Google Speech Recognition.")

@bot.command()
async def history(ctx):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user, text, timestamp FROM voice_messages ORDER BY timestamp DESC LIMIT 10")
    messages = cursor.fetchall()
    conn.close()

    if messages:
        history_text = "\n".join([f"{user} ({timestamp}): {text}" for user, text, timestamp in messages])
        await ctx.send(f"Last 10 voice messages:\n{history_text}")
    else:
        await ctx.send("No voice messages recorded yet.")



bot.run(" ")
