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

# Configure yt-dlp for best results
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'ignoreerrors': False,
    'force_generic_extractor': False,
    'cookiefile': None,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

@bot.event
async def on_ready():
    print(f'✅ Reso is online as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!play song"))

@bot.command(name='join')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send('❌ Join a voice channel first!')
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect(self_deaf=True)
    await ctx.send(f'✅ Joined {channel.name}')

@bot.command(name='play')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send('❌ Join a voice channel first!')
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(1)
    
    await ctx.send(f'🔍 Searching for: {search}')
    
    try:
        # Method 1: Try direct download URL for specific songs
        song_urls = {
            'despacito': 'https://www.youtube.com/watch?v=kJQP7kiw5Fk',
            'shape of you': 'https://www.youtube.com/watch?v=JGwWNGJdvx8',
            'believer': 'https://www.youtube.com/watch?v=7wtfhZwyrcc',
            'see you again': 'https://www.youtube.com/watch?v=RgKAFK5djSk',
            'faded': 'https://www.youtube.com/watch?v=60ItHLz5WEA',
        }
        
        # Check if it's a known song
        search_lower = search.lower()
        if search_lower in song_urls:
            url = song_urls[search_lower]
        elif search.startswith('http'):
            url = search
        else:
            # Search YouTube
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch5:{search}", download=False)
                if info and 'entries' in info and len(info['entries']) > 0:
                    url = info['entries'][0]['webpage_url']
                    title = info['entries'][0]['title']
                    await ctx.send(f'✅ Found: {title}')
                else:
                    await ctx.send('❌ No results found. Try a different search term.')
                    return
        
        # Download and play the audio
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Unknown')
            
            # Play the audio
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1',
                'options': '-vn'
            }
            
            audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            audio = discord.PCMVolumeTransformer(audio_source, volume=0.5)
            
            if ctx.voice_client.is_playing():
                await ctx.send(f'📝 Added to queue: **{title}**')
            else:
                ctx.voice_client.play(audio)
                await ctx.send(f'🎵 Now playing: **{title}**')
                await ctx.send('💡 Tip: Use !volume 100 for higher volume')
                
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)}')
        await ctx.send('Try using !play despacito or !play https://youtu.be/kJQP7kiw5Fk')

@bot.command(name='volume')
async def volume(ctx, vol: int):
    if ctx.voice_client and ctx.voice_client.source:
        vol = max(0, min(150, vol))
        ctx.voice_client.source.volume = vol / 100
        await ctx.send(f'🔊 Volume set to {vol}%')

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

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='songs')
async def list_songs(ctx):
    """List working songs"""
    await ctx.send('**Working songs:**\n!play despacito\n!play shape of you\n!play believer\n!play see you again\n!play faded')

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not set!')
        exit(1)
    bot.run(token)
