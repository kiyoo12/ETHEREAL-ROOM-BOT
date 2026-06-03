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
async def on_message(message):
    global last_played_song
    
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            desc = embed.description or ""
            title = embed.title or ""
            full_text = desc + " " + title
            
            if "started playing" in full_text.lower():
                raw = full_text.split("Started playing")[-1].strip()
                
                # FILTER GALAK BERDASARKAN JUDUL
                # Tambahin kata-kata yang sering muncul di video YouTube kamu
                banned = ["Official Video", "Guna Warma", "Nosstress", "Full Album", "Tanpa Iklan"]
                if any(b.lower() in raw.lower() for b in banned):
                    return # Langsung diam kalau kena filter

                # PROSES LIRIK
                clean_title = re.sub(r'[\(\[].*?[\)\]]', '', raw).split(" by ")[0].strip()
                
                if clean_title != last_played_song:
                    last_played_song = clean_title
                    await message.channel.send(f"Auto-Sync (Playing): {clean_title}")
                    
                    song = genius.search_song(clean_title)
                    if song:
                        await message.channel.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
                    else:
                        await message.channel.send("Lirik tidak ketemu.")
    
    await bot.process_commands(message)

bot.run(TOKEN)
