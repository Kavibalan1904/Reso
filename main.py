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
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')
    print(f'Connected to {len(bot.guilds)} servers')
    await bot.change_presence(activity=discord.Game(name="!play | !join"))

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
            await channel.connect(self_deaf=True)
        
        await ctx.send(f'✅ Joined **{channel.name}**')
        print(f'Joined voice channel: {channel.name}')
    except Exception as e:
        await ctx.send(f'❌ Failed to join: {str(e)[:100]}')
        print(f'Join error: {e}')

@bot.command(name='play')
async def play(ctx, *, song):
    """Play a song from YouTube"""
    if not ctx.author.voice:
        await ctx.send('❌ Join a voice channel first with `!join`')
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(2)
    
    await ctx.send(f'🔍 Searching for **{song}**...')
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Search for the song
            info = ydl.extract_info(f"ytsearch:{song}", download=False)
            
            if info and 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                title = video.get('title', 'Unknown')
                url = video.get('webpage_url')
                
                # Get the actual audio URL
                audio_info = ydl.extract_info(url, download=False)
                
                # Get audio stream URL
                audio_url = audio_info.get('url')
                if not audio_url and 'formats' in audio_info:
                    for f in audio_info['formats']:
                        if f.get('acodec') != 'none':
                            audio_url = f.get('url')
                            break
                
                if audio_url:
                    # Play the audio
                    ffmpeg_options = {'options': '-vn'}
                    player = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
                    volume_player = discord.PCMVolumeTransformer(player, volume=0.5)
                    
                    if ctx.voice_client.is_playing():
                        ctx.voice_client.stop()
                    
                    ctx.voice_client.play(volume_player)
                    await ctx.send(f'🎵 **Now playing:** {title}')
                    await ctx.send('💡 Tip: Use `!volume 100` for max volume')
                else:
                    await ctx.send('❌ Could not get audio stream')
            else:
                await ctx.send('❌ No results found. Try a different song name.')
                
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)[:150]}')
        print(f'Play error details: {e}')

@bot.command(name='volume')
async def volume(ctx, vol: int = None):
    """Set volume (0-150) or show current"""
    if not ctx.voice_client or not ctx.voice_client.source:
        await ctx.send('❌ Nothing is playing right now')
        return
    
    if vol is None:
        current = int(ctx.voice_client.source.volume * 100)
        await ctx.send(f'🔊 Current volume: **{current}%**')
        return
    
    vol = max(0, min(150, vol))
    ctx.voice_client.source.volume = vol / 100
    await ctx.send(f'🔊 Volume set to **{vol}%**')

@bot.command(name='pause')
async def pause(ctx):
    """Pause current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('⏸️ Paused')

@bot.command(name='resume')
async def resume(ctx):
    """Resume current song"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('▶️ Resumed')

@bot.command(name='skip')
async def skip(ctx):
    """Skip current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏭️ Skipped')

@bot.command(name='stop')
async def stop(ctx):
    """Stop and leave voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('🛑 Stopped and left the voice channel')

@bot.command(name='ping')
async def ping(ctx):
    """Check bot response time"""
    await ctx.send(f'🏓 Pong! **{round(bot.latency * 1000)}ms**')

@bot.command(name='info')
async def info(ctx):
    """Show bot information"""
    embed = discord.Embed(
        title="🎵 Reso Music Bot",
        description="Your personal music bot for Discord!",
        color=discord.Color.blue()
    )
    embed.add_field(name="Commands", value="`!join`, `!play`, `!pause`, `!resume`, `!skip`, `!stop`, `!volume`, `!ping`", inline=False)
    embed.add_field(name="Example", value="`!play despacito`", inline=False)
    await ctx.send(embed=embed)

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN environment variable not set!')
        exit(1)
    
    print('Starting Reso bot...')
    bot.run(token)
