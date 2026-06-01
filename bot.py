import discord
from discord.ext import commands
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')

# Setup Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Setup Genius
genius = lyricsgenius.Genius(GENIUS_TOKEN)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="!lirik <judul lagu>"))
    print(f'ETHEREAL ROOM Bot Lirik udah ON, {bot.user} siap beraksi!')

# --- EVENT AUTO-SYNC ---
@bot.event
async def on_message(message):
    # Biar bot nggak ngerespon pesannya sendiri
    if message.author == bot.user:
        await bot.process_commands(message)
        return

    # Cek apakah pesan dari Jockie Music dan di channel yang ngandung kata "play-music"
    if "Jockie" in message.author.name and message.embeds and "play-music" in message.channel.name.lower():
        embed = message.embeds[0]
        # Ambil semua teks dari embed (deskripsi + fields)
        search_text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
        
        if "Started playing" in search_text:
            # Ambil teks setelah "Started playing"
            raw_title = search_text.split("Started playing")[-1].strip()
            
            # --- TEKNIK PEMBERSIHAN ---
            clean_title = re.sub(r'\(.*?\)', '', raw_title)
            clean_title = clean_title.split(" by ")[0].strip()
            clean_title = clean_title.replace(" - ", " ").strip()
            
            await message.channel.send(f"Auto-Sync: {clean_title}...")
            
            # --- PENCARIAN DENGAN FALLBACK ---
            song = genius.search_song(clean_title)
            if not song:
                song = genius.search_song(raw_title)

            if song:
                lirik_text = song.lyrics[:2000] 
                embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
                embed.set_footer(text=f"Artist: {song.artist}")
                await message.channel.send(embed=embed)
            else:
                await message.channel.send(f"Aduh, lirik buat '{clean_title}' nggak ketemu di Genius.")

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
                clean_title = clean_title.split(" by ")[0].strip()
                clean_title = clean_title.replace(" - ", " ").strip()
                
                await ctx.send(f"Sync Manual: {clean_title}...")
                song = genius.search_song(clean_title)
                if not song: song = genius.search_song(raw_title)
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
