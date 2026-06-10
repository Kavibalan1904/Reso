import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Simple queue system
queues = {}

@bot.event
async def on_ready():
    print(f'✅ Reso is online as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!play song"))

@bot.command(name='join')
async def join(ctx):
    """Join your voice channel"""
    if not ctx.author.voice:
        await ctx.send('❌ You must be in a voice channel!')
        return
    
    channel = ctx.author.voice.channel
    
    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect(self_deaf=True, self_mute=False)
        
        await ctx.send(f'✅ Connected to **{channel.name}** and deafened')
    except Exception as e:
        await ctx.send(f'❌ Failed to connect: {str(e)}')

@bot.command(name='play')
async def play(ctx, *, song_name):
    """Play a song from YouTube"""
    if not ctx.author.voice:
        await ctx.send('❌ Join a voice channel first with `!join`')
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)
    
    await ctx.send(f'🔍 Searching for **{song_name}**...')
    
    # Options for yt-dlp
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Search for the song
            search_results = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            
            if 'entries' in search_results and search_results['entries']:
                video = search_results['entries'][0]
                url = video['webpage_url']
                title = video['title']
                
                # Get the audio URL
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                
                # Create audio player
                ffmpeg_opts = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                
                player = discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts)
                player = discord.PCMVolumeTransformer(player, volume=0.5)
                
                # Stop current song if playing
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                
                # Play the song
                ctx.voice_client.play(player)
                await ctx.send(f'🎵 Now playing: **{title}**')
                await ctx.send(f'🔊 Type `!volume 100` to increase volume')
            else:
                await ctx.send('❌ No results found!')
                
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)[:200]}')
        print(f'Play error: {e}')

@bot.command(name='volume')
async def volume(ctx, vol: int):
    """Set volume (0-150)"""
    if ctx.voice_client and ctx.voice_client.source:
        vol = max(0, min(150, vol))
        ctx.voice_client.source.volume = vol / 100
        await ctx.send(f'🔊 Volume set to **{vol}%**')
    else:
        await ctx.send('❌ Nothing is playing!')

@bot.command(name='pause')
async def pause(ctx):
    """Pause the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('⏸️ Paused')
    else:
        await ctx.send('❌ Nothing is playing!')

@bot.command(name='resume')
async def resume(ctx):
    """Resume the current song"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('▶️ Resumed')
    else:
        await ctx.send('❌ Nothing is paused!')

@bot.command(name='stop')
async def stop(ctx):
    """Stop playback and disconnect"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('🛑 Stopped and disconnected')
    else:
        await ctx.send('❌ I\'m not in a voice channel!')

@bot.command(name='skip')
async def skip(ctx):
    """Skip the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏭️ Skipped!')
    else:
        await ctx.send('❌ Nothing is playing!')

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f'🏓 Pong! **{round(bot.latency * 1000)}ms**')

@bot.command(name='test')
async def test(ctx):
    """Test if bot is working"""
    await ctx.send('✅ Bot is working! Try `!join` then `!play despacito`')

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN environment variable not set!')
        exit(1)
    bot.run(token)
