import discord
from discord.ext import commands
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
TARGET_CHANNEL_ID = 1510507327785144470 # ID channel lu

# Setup Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@bot.event
async def on_ready():
    print(f'Bot Ethereal sudah ON dan siap beraksi secara Instan!')

@bot.event
async def on_message(message):
    global last_played_song
    
    # Bot cuma dengerin pesan dari Jockie dan di channel yang kita mau
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            # Ambil semua teks dari embed
            text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
            
            if "Started playing" in text:
                # Bersihin nama lagu
                raw = text.split("Started playing")[-1].strip()
                title = re.sub(r'\(.*?\)', '', raw).split(" by ")[0].strip()
                
                # Biar nggak dobel kalau Jockie nge-post berkali-kali
                if title != last_played_song:
                    last_played_song = title
                    # Kirim notifikasi instan
                    await message.channel.send(f"Auto-Sync (Playing): {title}")
                    
                    # Cari lirik
                    song = genius.search_song(title)
                    if song:
                        embed_lirik = discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB)
                        embed_lirik.set_footer(text=f"Artist: {song.artist}")
                        await message.channel.send(embed=embed_lirik)
    
    # WAJIB: Biar command !lirik tetep bisa dipake
    await bot.process_commands(message)

@bot.command()
async def lirik(ctx, *, judul_lagu):
    song = genius.search_song(judul_lagu)
    if song:
        await ctx.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
    else:
        await ctx.send("Lirik tidak ketemu.")

bot.run(TOKEN)
