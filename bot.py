import discord
from discord.ext import commands
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID', 0))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@bot.event
async def on_ready():
    print(f'Bot Ethereal Ready!')

@bot.event
async def on_message(message):
    global last_played_song
    
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
            
            if "Started playing" in text:
                # Logic awal yang terbukti stabil
                raw = text.split("Started playing")[-1].strip()
                title = re.sub(r'\(.*?\)', '', raw).split(" by ")[0].strip()
                
                if title != last_played_song:
                    last_played_song = title
                    await message.channel.send(f"Auto-Sync (Playing): {title}")
                    
                    song = genius.search_song(title)
                    if song:
                        embed_lirik = discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB)
                        embed_lirik.set_footer(text=f"Artist: {song.artist}")
                        await message.channel.send(embed=embed_lirik)
                    else:
                        await message.channel.send("Lyrics not found")
    
    await bot.process_commands(message)

bot.run(TOKEN)
