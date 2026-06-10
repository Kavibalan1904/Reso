import discord
from discord.ext import commands
import wavelink
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Reso is online as {bot.user}')
    print(f'Connected to {len(bot.guilds)} servers')
    
    # Setup Lavalink
    try:
        node = wavelink.Node(
            uri='http://localhost:2333',
            password='youshallnotpass'
        )
        await wavelink.Pool.connect(client=bot, nodes=[node])
        print('✅ Connected to Lavalink')
    except Exception as e:
        print(f'⚠️ Lavalink connection failed: {e}')
        print('Music commands will not work until Lavalink connects')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='join')
async def join(ctx):
    """Bot joins your voice channel"""
    if not ctx.author.voice:
        await ctx.send('❌ You need to be in a voice channel first!')
        return
    
    channel = ctx.author.voice.channel
    
    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        await ctx.send(f'✅ Joined {channel.mention}')
        print(f'Joined voice channel: {channel.name}')
    except Exception as e:
        await ctx.send(f'❌ Failed to join: {str(e)}')
        print(f'Join error: {e}')

@bot.command(name='play')
async def play(ctx, *, search: str):
    """Play a song from YouTube"""
    # Check if user is in voice channel
    if not ctx.author.voice:
        await ctx.send('❌ You need to be in a voice channel first!')
        return
    
    # Join voice channel if not already in one
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(1)  # Wait for connection
    
    vc: wavelink.Player = ctx.voice_client
    
    # Check Lavalink connection
    if not vc.node or not vc.node.is_connected:
        await ctx.send('❌ Music player is initializing. Please wait 10 seconds and try again.')
        return
    
    await ctx.send(f'🔍 Searching for: {search}')
    
    try:
        # Search for tracks
        tracks = await wavelink.YouTubeTrack.search(search, return_first=True)
        
        if not tracks:
            await ctx.send('❌ No results found!')
            return
        
        # Play or queue
        if vc.is_playing():
            await vc.queue.put_wait(tracks)
            await ctx.send(f'📝 Added to queue: **{tracks.title}**')
        else:
            await vc.play(tracks)
            await ctx.send(f'🎵 Now playing: **{tracks.title}**')
            
    except Exception as e:
        await ctx.send(f'❌ Error playing: {str(e)}')
        print(f'Play error: {e}')

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

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('🛑 Stopped')

@bot.command(name='volume')
async def volume(ctx, vol: int):
    if ctx.voice_client:
        if 0 <= vol <= 150:
            await ctx.voice_client.set_volume(vol)
            await ctx.send(f'🔊 Volume set to {vol}%')
        else:
            await ctx.send('❌ Volume must be between 0 and 150')

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not set!')
        exit(1)
    bot.run(token)
