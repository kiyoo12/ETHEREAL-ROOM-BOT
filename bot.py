import discord
from discord.ext import commands, tasks
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Penting untuk akses channel
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@tasks.loop(seconds=15)
async def check_music():
    global last_played_song
    # Cari channel yang namanya mengandung "play-music" tanpa bikin bot crash
    channels = [ch for ch in bot.get_all_channels() if ch.name and "play-music" in ch.name.lower()]
    
    if not channels:
        return # Channel belum ketemu, skip dulu loop-nya
    
    channel = channels[0]
    try:
        async for message in channel.history(limit=5):
            if "Jockie" in message.author.name and message.embeds:
                embed = message.embeds[0]
                search_text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
                
                if "Started playing" in search_text:
                    raw_title = search_text.split("Started playing")[-1].strip()
                    clean_title = re.sub(r'\(.*?\)', '', raw_title).split(" by ")[0].strip().replace(" - ", " ").strip()
                    
                    if clean_title != last_played_song:
                        last_played_song = clean_title
                        await channel.send(f"Auto-Sync: {clean_title}...")
                        
                        # Cari dengan filter artis
                        artist_name = raw_title.split(" by ")[-1].strip() if " by " in raw_title else ""
                        song = genius.search_song(clean_title, artist=artist_name)
                        if not song: song = genius.search_song(clean_title)
                        
                        if song:
                            lirik_text = song.lyrics[:2000]
                            embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
                            embed.set_footer(text=f"Artist: {song.artist}")
                            await channel.send(embed=embed)
                        else:
                            await channel.send(f"Lirik '{clean_title}' tidak ketemu.")
                    break
    except Exception as e:
        print(f"Error di loop: {e}")

@bot.event
async def on_ready():
    if not check_music.is_running():
        check_music.start()
    print(f'ETHEREAL ROOM Bot Lirik udah ON!')

@bot.command()
async def lirik(ctx, *, judul_lagu):
    song = genius.search_song(judul_lagu)
    if song:
        lirik_text = song.lyrics[:2000]
        embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Lirik tidak ketemu.")

bot.run(TOKEN)
