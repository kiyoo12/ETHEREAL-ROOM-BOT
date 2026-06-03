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
    print(f'Bot Ethereal sudah ON!')

@bot.event
async def on_message(message):
    global last_played_song
    
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            
            # Gabung semua sumber teks untuk dicek
            title_text = embed.title or ""
            desc_text = embed.description or ""
            url_text = embed.url or ""
            provider_name = embed.provider.name.lower() if embed.provider and embed.provider.name else ""
            
            # Gabungkan semuanya dalam satu string untuk pencarian keyword
            full_content = (title_text + " " + desc_text + " " + url_text + " " + provider_name).lower()
            
            # --- FILTER SUPER GALAK ---
            # Kalau ada kata 'youtube' di manapun, atau link youtube, langsung STOP
            if "youtube" in full_content or "youtu.be" in full_content:
                print("Konten YouTube terdeteksi, skip lirik.")
                return 

            # Cek apakah ini pesan "Started playing"
            # Jockie kadang naro ini di description atau di title
            if "started playing" in (desc_text.lower() + " " + title_text.lower()):
                
                # Bersihin judul (Hapus [], (), dan kata "by")
                raw = (desc_text if "started playing" in desc_text.lower() else title_text)
                raw = raw.replace("Started playing", "").replace("started playing", "").strip()
                clean_title = re.sub(r'[\(\[].*?[\)\]]', '', raw)
                title = clean_title.split(" by ")[0].strip()
                
                if title and title != last_played_song:
                    last_played_song = title
                    await message.channel.send(f"Auto-Sync (Playing): {title}")
                    
                    song = genius.search_song(title)
                    if song:
                        embed_lirik = discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB)
                        embed_lirik.set_footer(text=f"Artist: {song.artist}")
                        await message.channel.send(embed=embed_lirik)
                    else:
                        await message.channel.send("Lirik tidak ketemu.")
    
    await bot.process_commands(message)

bot.run(TOKEN)
