import discord
from discord.ext import commands, tasks
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
# ID Channel lu yang udah bener
TARGET_CHANNEL_ID = 1510507327785144470 

# Setup Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@tasks.loop(seconds=3)
async def check_music():
    global last_played_song
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    
    if not channel:
        print(f"DEBUG: Bot tidak bisa menemukan channel dengan ID {TARGET_CHANNEL_ID}")
        return
    
    # Ambil 5 pesan terakhir
    async for message in channel.history(limit=5):
        # Cek pesan dari Jockie Music yang punya embed
        if "Jockie" in message.author.name and message.embeds:
            embed = message.embeds[0]
            # Gabungin deskripsi dan fields buat dicari teksnya
            text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
            
            if "Started playing" in text:
                # Log buat debugging di Railway
                print(f"DEBUG: Jockie sedang memutar: {text}")
                
                raw = text.split("Started playing")[-1].strip()
                title = re.sub(r'\(.*?\)', '', raw).split(" by ")[0].strip()
                
                # Biar nggak spam
                if title != last_played_song:
                    last_played_song = title
                    await channel.send(f"Auto-Sync: {title}...")
                    
                    # Cari lagu
                    song = genius.search_song(title)
                    if song:
                        lirik = song.lyrics[:2000]
                        embed = discord.Embed(title=song.title, description=lirik, color=0x87CEEB)
                        embed.set_footer(text=f"Artist: {song.artist}")
                        await channel.send(embed=embed)
                    else:
                        await channel.send(f"Waduh, lirik buat '{title}' nggak ketemu.")
                break

@bot.event
async def on_ready():
    if not check_music.is_running():
        check_music.start()
    print(f'Bot Ethereal sudah ON dan siap memantau!')

@bot.command()
async def lirik(ctx, *, judul_lagu):
    song = genius.search_song(judul_lagu)
    if song:
        await ctx.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
    else:
        await ctx.send("Lirik tidak ketemu.")

bot.run(TOKEN)
