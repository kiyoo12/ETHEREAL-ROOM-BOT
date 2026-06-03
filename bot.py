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
    print(f'Bot Ethereal sudah ON dan dalam mode Bandel!')

@bot.event
async def on_message(message):
    global last_played_song
    
    # Filter author dan channel
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        
        # Gabungkan semua teks embed yang mungkin ada
        embed_text = ""
        if message.embeds:
            embed_text = (message.embeds[0].description or "") + " " + (message.embeds[0].title or "")
        
        full_text = message.content + " " + embed_text
        
        # Mode Bandel: Asal ada "Started playing", sikat!
        if "started playing" in full_text.lower():
            # Ambil bagian judul
            raw = full_text.lower().split("started playing")[-1].strip()
            # Pembersih judul (Hapus [], (), dan kata "by")
            clean_title = re.sub(r'[\(\[].*?[\)\]]', '', raw).split(" by ")[0].strip()
            
            if clean_title and clean_title != last_played_song:
                last_played_song = clean_title
                await message.channel.send(f"Auto-Sync (Playing): {clean_title}")
                
                # Cari lirik
                song = genius.search_song(clean_title)
                if song:
                    await message.channel.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
                else:
                    await message.channel.send("Lirik tidak ketemu.")
    
    await bot.process_commands(message)

@bot.command()
async def lirik(ctx, *, judul_lagu):
    song = genius.search_song(judul_lagu)
    if song:
        await ctx.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
    else:
        await ctx.send("Lirik tidak ketemu.")

bot.run(TOKEN)
