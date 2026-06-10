import discord
from discord.ext import commands
import wavelink
import os
import sys
import asyncio
from dotenv import load_dotenv

# Force stdout to flush immediately
sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Reso is online as {bot.user}', flush=True)
    print(f'Connected to {len(bot.guilds)} servers', flush=True)
    
    # Setup Lavalink
    try:
        node = wavelink.Node(
            uri='http://localhost:2333',
            password='youshallnotpass'
        )
        await wavelink.Pool.connect(client=bot, nodes=[node])
        print('✅ Connected to Lavalink', flush=True)
    except Exception as e:
        print(f'⚠️ Lavalink connection failed: {e}', flush=True)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='join')
async def join(ctx):
    """Bot joins your voice channel and deafens itself"""
    if not ctx.author.voice:
        await ctx.send('❌ You need to be in a voice channel first!')
        return
    
    channel = ctx.author.voice.channel
    
    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            # Connect with self_deaf=True
            await channel.connect(self_deaf=True)
        
        await ctx.send(f'✅ Joined {channel.mention} and deafened')
        print(f'Joined voice channel: {channel.name}', flush=True)
    except Exception as e:
        await ctx.send(f'❌ Failed to join: {str(e)}')
        print(f'Join error: {e}', flush=True)

@bot.command(name='play')
async def play(ctx, *, search: str):
    """Play a song from YouTube"""
    if not ctx.author.voice:
        await ctx.send('❌ You need to be in a voice channel first!')
        return
    
    # Join voice channel if not already in one
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(2)
    
    vc = ctx.voice_client
    
    await ctx.send(f'🔍 Searching for: {search}')
    print(f'Searching for: {search}', flush=True)
    
    try:
        # Search for tracks
        tracks = await wavelink.Playable.search(search)
        
        if not tracks:
            await ctx.send('❌ No results found!')
            return
        
        # Get the first track
        track = tracks[0] if isinstance(tracks, list) else tracks
        print(f'Found track: {track.title}', flush=True)
        
        if vc.is_playing():
            await vc.queue.put_wait(track)
            await ctx.send(f'📝 Added to queue: **{track.title}**')
        else:
            await vc.play(track)
            await ctx.send(f'🎵 Now playing: **{track.title}**')
            await ctx.send(f'🔊 Current volume: {vc.volume}% (use !volume 100 to increase)')
            print(f'Now playing: {track.title}', flush=True)
            
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)}')
        print(f'Play error: {e}', flush=True)

@bot.command(name='volume')
async def volume(ctx, vol: int):
    if ctx.voice_client:
        if 0 <= vol <= 150:
            await ctx.voice_client.set_volume(vol)
            await ctx.send(f'🔊 Volume set to {vol}%')
            print(f'Volume set to {vol}%', flush=True)
        else:
            await ctx.send('❌ Volume must be between 0 and 150')

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('🛑 Stopped and left channel')
        print('Stopped and left channel', flush=True)

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.pause()
        await ctx.send('⏸️ Paused')

@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        await ctx.voice_client.resume()
        await ctx.send('▶️ Resumed')

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.stop()
        await ctx.send('⏭️ Skipped')

@bot.command(name='test')
async def test(ctx):
    """Test if bot is responding"""
    await ctx.send('✅ Bot is working! Try !join then !play songname')

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not set!', flush=True)
        exit(1)
    print('Starting bot...', flush=True)
    bot.run(token)
