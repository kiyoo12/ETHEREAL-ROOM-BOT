import discord
from discord.ext import commands
import lyricsgenius
import os

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
                # Ambil teks setelah "Started playing"
                raw_title = search_text.split("Started playing")[-1].strip()
                
                # --- TEKNIK PEMBERSIHAN ---
                # Kalau ada kata "by", kita potong dan ambil bagian depannya saja
                # Contoh: "Semua Aku Dirayakan by Nadin Amizah" -> "Semua Aku Dirayakan"
                clean_title = raw_title.split(" by ")[0].strip()
                
                await ctx.send(f"Ketemu! Jockie lagi muter: {clean_title}. Lagi nyari liriknya...")
                
                # Langsung panggil pencarian lirik dengan judul bersih
                song = genius.search_song(clean_title)
                if song:
                    lirik_text = song.lyrics[:2000] 
                    embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
                    embed.set_footer(text=f"Artist: {song.artist}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Aduh, lirik buat '{clean_title}' nggak ketemu di Genius, Ky.")
                
                found = True
                break
    
    if not found:
        await ctx.send("Waduh, Jockie-nya masih sembunyi nih.")

bot.run(TOKEN)
