import discord
from discord.ext import commands
import lyricsgenius
import os
import re
import random

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID', 0))

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@bot.event
async def on_ready():
    print(f'Bot Ethereal sudah ON!')
    await bot.change_presence(activity=None)

@bot.event
async def on_message(message):
    global last_played_song
    
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            content = f"{embed.title or ''} {embed.description or ''}"
            for field in embed.fields:
                content += f" {field.name} {field.value}"
            
            if "Started playing" in content:
                raw = content.split("Started playing")[-1].strip()
                title = re.split(r'\(https://| by ', raw)[0].strip()
                title = title.replace("*", "").replace("[", "").replace("]", "").strip()

                if title and title != last_played_song:
                    last_played_song = title
                    
                    # 1. Konfirmasi Auto-Sync
                    await message.channel.send(f"Auto-Sync (Playing): **{title}**")
                    
                    # 2. Update status "Listening to"
                    activity = discord.Activity(type=discord.ActivityType.listening, name=title)
                    await bot.change_presence(activity=activity)
                    
                    # 3. FITUR GJ (RANDOMIZER MOOD)
                    moods = [
                        "Feeling: {title} 🎧", "Currently loving: {title} ✨", 
                        "Deep in: {title} 🌌", "Thinking about: {title} 💭",
                        "Floating with: {title} ☁️", "Healing with: {title} 🩹",
                        "Drowning in: {title} 🌊", "Lost in: {title} 🌙"
                    ]
                    status_text = random.choice(moods).format(title=title)
                    await message.channel.send(f"Status: *{status_text}*")
                    
                  # 4. Cari lirik
                    song = genius.search_song(title)
                    if song:
                        vibe_colors = [
                            0x87CEEB, 0xD8BFD8, 0xF08080, 
                            0x778899, 0xFFE4B5, 0xB0C4DE
                        ]
                        random_color = random.choice(vibe_colors)
                        
                        embed_lirik = discord.Embed(
                            title=song.title, 
                            description=song.lyrics[:2000], 
                            color=random_color
                        )
                        embed_lirik.set_footer(text=f"Artist: {song.artist}")
                        await message.channel.send(embed=embed_lirik)
                    else:
                        await message.channel.send(f"Lyrics not found for: {title}")
    
    await bot.process_commands(message)

bot.run(TOKEN)
