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

# Fix yt-dlp for YouTube's changes
youtube_dl.utils.bug_reports_message = lambda: ''

ydl_opts = {
    'format': 'bestaudio',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'ignoreerrors': True,
    'source_address': '0.0.0.0',
    'force_generic_extractor': False,
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')
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
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send('❌ Join a voice channel first with `!join`')
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)
    
    await ctx.send(f'🔍 Searching: {query}')
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Search or direct URL
            if query.startswith('http'):
                info = ydl.extract_info(query, download=False)
                title = info.get('title', 'Unknown')
            else:
                # Search
                search = ydl.extract_info(f"ytsearch:{query}", download=False)
                if 'entries' in search and search['entries']:
                    info = search['entries'][0]
                    title = info.get('title', 'Unknown')
                else:
                    await ctx.send('❌ No results found')
                    return
            
            # Get audio URL - Try different approaches
            audio_url = None
            
            # Try to get best audio format
            if 'url' in info:
                audio_url = info['url']
            elif 'formats' in info:
                # Find best audio-only format
                for f in info['formats']:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        audio_url = f.get('url')
                        break
                
                # If no audio-only, get best audio from any format
                if not audio_url:
                    for f in info['formats']:
                        if f.get('acodec') != 'none':
                            audio_url = f.get('url')
                            break
            
            if not audio_url:
                await ctx.send('❌ Could not extract audio URL')
                return
            
            # Create audio player
            ffmpeg_opts = {
                'before_options': '-reconnect 1 -reconnect_streamed 1',
                'options': '-vn'
            }
            
            player = discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts)
            volume_player = discord.PCMVolumeTransformer(player, volume=0.5)
            
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            
            ctx.voice_client.play(volume_player)
            await ctx.send(f'🎵 Now playing: **{title}**')
            await ctx.send('💡 Use `!volume 100` for max volume')
            
    except Exception as e:
        error_msg = str(e)
        if 'Requested format is not available' in error_msg:
            await ctx.send('❌ YouTube format error. Try a different song name.')
        else:
            await ctx.send(f'❌ Error: {error_msg[:100]}')
        
        print(f'Error: {error_msg}')

@bot.command(name='volume')
async def volume(ctx, vol: int = None):
    if not ctx.voice_client or not ctx.voice_client.source:
        await ctx.send('❌ Nothing playing')
        return
    
    if vol is None:
        current = int(ctx.voice_client.source.volume * 100)
        await ctx.send(f'🔊 Current volume: {current}%')
        return
    
    vol = max(0, min(150, vol))
    ctx.voice_client.source.volume = vol / 100
    await ctx.send(f'🔊 Volume: {vol}%')

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

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('🛑 Stopped')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
