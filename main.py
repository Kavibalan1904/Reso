import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'ignoreerrors': True,
    'default_search': 'ytsearch',
}

@bot.event
async def on_ready():
    print(f'✅ Reso is online as {bot.user}')
    print(f'Connected to {len(bot.guilds)} servers')
    await bot.change_presence(activity=discord.Game(name="!play to listen"))

@bot.command(name='join')
async def join(ctx):
    """Bot joins your voice channel"""
    if not ctx.author.voice:
        await ctx.send('❌ You need to be in a voice channel first!')
        return
    
    channel = ctx.author.voice.channel
    
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect(self_deaf=True)
    
    await ctx.send(f'✅ Joined {channel.mention}')

@bot.command(name='play')
async def play(ctx, *, query):
    """Play a song from YouTube"""
    if not ctx.author.voice:
        await ctx.send('❌ You need to be in a voice channel first!')
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(1)
    
    # Show typing indicator while searching
    async with ctx.typing():
        await ctx.send(f'🔍 Searching: {query}')
        
        try:
            # Use yt-dlp to extract audio URL
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                # Search or get direct URL
                if query.startswith('http://') or query.startswith('https://'):
                    info = ydl.extract_info(query, download=False)
                else:
                    # Search for the video
                    search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
                    if search_results and 'entries' in search_results and search_results['entries']:
                        info = search_results['entries'][0]
                    else:
                        await ctx.send('❌ No results found!')
                        return
                
                if not info:
                    await ctx.send('❌ Could not find the song!')
                    return
                
                # Get the best audio URL
                url = info.get('url', info.get('webpage_url', None))
                title = info.get('title', 'Unknown Title')
                
                if not url:
                    await ctx.send('❌ Could not extract audio URL!')
                    return
                
                # Create audio source
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                
                audio_source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
                audio = discord.PCMVolumeTransformer(audio_source, volume=0.5)
                
                # Play the audio
                if ctx.voice_client.is_playing():
                    await ctx.send(f'📝 Added to queue: **{title}**')
                else:
                    def after_play(error):
                        if error:
                            print(f'Playback error: {error}')
                    
                    ctx.voice_client.play(audio, after=after_play)
                    await ctx.send(f'🎵 Now playing: **{title}**')
                    
        except Exception as e:
            await ctx.send(f'❌ Error: {str(e)}')
            print(f'Play error details: {e}')

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('⏸️ Paused')

@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('▶️ Resumed')

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏭️ Skipped')

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send('🛑 Stopped')

@bot.command(name='volume')
async def volume(ctx, vol: int):
    if ctx.voice_client and ctx.voice_client.source:
        volume_level = max(0, min(150, vol)) / 100
        ctx.voice_client.source.volume = volume_level
        await ctx.send(f'🔊 Volume set to {vol}%')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not set!')
        exit(1)
    bot.run(token)
