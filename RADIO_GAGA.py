import discord
from discord.ext import commands
import asyncio
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

queue = []

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command(name="play", aliases=["p"])
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if not voice_client:
        voice_client = await voice_channel.connect()

    with yt_dlp.YoutubeDL({'quiet': True, 'format': 'bestaudio'}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "Unknown Title")
        audio_url = info['url']

    queue.append({"url": url, "title": title})

    if not voice_client.is_playing():
        await play_next(ctx, voice_client)

async def play_next(ctx, voice_client):
    if not queue:
        await voice_client.disconnect()
        return

    current = queue[0]
    url = current["url"]

    with yt_dlp.YoutubeDL({'quiet': True, 'format': 'bestaudio'}) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    source = await discord.FFmpegOpusAudio.from_probe(audio_url, method='fallback')
    voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx, voice_client), bot.loop))
    await ctx.send(f"🎶 Reproduciendo: **{current['title']}**")
    queue.pop(0)

@bot.command(name="queue")
async def queue_(ctx):
    if not queue:
        await ctx.send("📭 No pending songs.")
    else:
        msg = "📜 Playlist:\n" + "\n".join(f"{i+1}. {song['title']}" for i, song in enumerate(queue))
        await ctx.send(msg)

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("⏸ Song paused.")

@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("▶️ Song resumed.")

@bot.command()
async def clear(ctx):
    queue.clear()
    await ctx.send("🗑 Queue cleared.")

# Poner en "" el token del bot.
bot.run("#")


#Bot hecho por LucasChiodin666
