import discord
from discord.ext import commands, tasks
import lyricsgenius
import os
import re

# ... (Config & Setup tetap sama)
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# Variabel buat nyimpen judul lagu terakhir biar gak spam lirik yang sama
last_played_song = ""

@tasks.loop(seconds=10) # Bot bakal ngecek channel tiap 10 detik
async def check_music():
    global last_played_song
    # Cari channel yang namanya mengandung "play-music"
    channel = discord.utils.get(bot.get_all_channels(), name="play-music") # Ganti kalau nama channel lu di discord ada simbolnya!
    # Kalo tetep gak kebaca, kita pake filter nama manual:
    # channel = [ch for ch in bot.get_all_channels() if "play-music" in ch.name.lower()][0]

    if channel:
        async for message in channel.history(limit=5):
            if "Jockie" in message.author.name and message.embeds:
                embed = message.embeds[0]
                search_text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
                
                if "Started playing" in search_text:
                    raw_title = search_text.split("Started playing")[-1].strip()
                    clean_title = re.sub(r'\(.*?\)', '', raw_title).split(" by ")[0].strip().replace(" - ", " ").strip()
                    
                    # Cek apakah lagu ini udah pernah kita cari
                    if clean_title != last_played_song:
                        last_played_song = clean_title
                        await channel.send(f"Auto-Sync: {clean_title}...")
                        
                        song = genius.search_song(clean_title, artist=(raw_title.split(" by ")[-1].strip() if " by " in raw_title else ""))
                        if not song: song = genius.search_song(clean_title)
                        
                        if song:
                            lirik_text = song.lyrics[:2000]
                            embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
                            embed.set_footer(text=f"Artist: {song.artist}")
                            await channel.send(embed=embed)
                        else:
                            await channel.send(f"Lirik '{clean_title}' nggak ketemu.")
                    break

@bot.event
async def on_ready():
    check_music.start() # Jalanin loop-nya pas bot nyala
    print(f'ETHEREAL ROOM Bot Lirik udah ON!')

# ... (sisa commands tetap sama)

    # WAJIB: Biar command manual (!lirik dan !sync) tetep jalan
    await bot.process_commands(message)

# --- COMMANDS ---
@bot.command()
async def lirik(ctx, *, judul_lagu):
    await ctx.send(f"Bentar, lagi nyari lirik buat: {judul_lagu}...")
    song = genius.search_song(judul_lagu)
    if song:
        lirik_text = song.lyrics[:2000] 
        embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
        embed.set_footer(text=f"Artist: {song.artist}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Waduh, liriknya nggak ketemu nih. Coba cek judulnya lagi ya")

@bot.command()
async def sync(ctx):
    found = False
    async for message in ctx.channel.history(limit=15):
        if "Jockie" in message.author.name and message.embeds:
            embed = message.embeds[0]
            search_text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
            if "Started playing" in search_text:
                raw_title = search_text.split("Started playing")[-1].strip()
                clean_title = re.sub(r'\(.*?\)', '', raw_title)
                artist_name = clean_title.split(" by ")[-1].strip() if " by " in clean_title else ""
                clean_title = clean_title.split(" by ")[0].strip()
                clean_title = clean_title.replace(" - ", " ").strip()
                
                await ctx.send(f"Sync Manual: {clean_title}...")
                song = genius.search_song(clean_title, artist=artist_name)
                if not song: song = genius.search_song(clean_title)
                if song:
                    lirik_text = song.lyrics[:2000] 
                    embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
                    embed.set_footer(text=f"Artist: {song.artist}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Lirik '{clean_title}' tidak ketemu.")
                found = True
                break
    if not found:
        await ctx.send("Waduh, Jockie-nya masih sembunyi nih.")

bot.run(TOKEN)
