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
    except Exception as e:
        await ctx.send(f'❌ Failed to join: {str(e)}')

@bot.command(name='play')
async def play(ctx, *, search: str):
    """Play a song from YouTube"""
    if not ctx.author.voice:
        await ctx.send('❌ You need to be in a voice channel first!')
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(1)
    
    vc: wavelink.Player = ctx.voice_client
    
    await ctx.send(f'🔍 Searching for: {search}')
    
    try:
        # Correct way to search in Wavelink 3.x
        tracks = await wavelink.Playable.search(search)
        
        if not tracks:
            await ctx.send('❌ No results found!')
            return
        
        # Get the first track
        track = tracks[0] if isinstance(tracks, list) else tracks
        
        if vc.is_playing():
            await vc.queue.put_wait(track)
            await ctx.send(f'📝 Added to queue: **{track.title}**')
        else:
            await vc.play(track)
            await ctx.send(f'🎵 Now playing: **{track.title}**')
            
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)}')
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
        await ctx.send('🛑 Stopped and left channel')

@bot.command(name='volume')
async def volume(ctx, vol: int):
    if ctx.voice_client:
        if 0 <= vol <= 150:
            await ctx.voice_client.set_volume(vol)
            await ctx.send(f'🔊 Volume set to {vol}%')
        else:
            await ctx.send('❌ Volume must be between 0 and 150')

@bot.command(name='queue')
async def show_queue(ctx):
    if not ctx.voice_client:
        await ctx.send('❌ Not in a voice channel')
        return
    
    vc: wavelink.Player = ctx.voice_client
    
    if not vc.queue:
        await ctx.send('📭 Queue is empty')
        return
    
    queue_list = list(vc.queue)
    queue_text = "**Current Queue:**\n"
    
    for i, track in enumerate(queue_list[:10], 1):
        queue_text += f"{i}. {track.title}\n"
    
    if len(queue_list) > 10:
        queue_text += f"\nAnd {len(queue_list) - 10} more..."
    
    await ctx.send(queue_text)

@bot.command(name='eq')
async def equalizer(ctx, preset: str = None):
    if not ctx.voice_client:
        await ctx.send('❌ Bot is not in a voice channel')
        return
    
    vc: wavelink.Player = ctx.voice_client
    
    presets = {
        'bass': [(0, 0.2), (1, 0.3), (2, 0.1)],
        'nightcore': [(0, 0.3), (1, 0.2)],
        'classical': [(0, 0.1), (1, -0.1)],
        'pop': [(0, 0.1), (1, 0.1), (2, 0.1)],
        'dance': [(0, 0.2), (1, 0.3), (2, 0.1)],
        'reset': []
    }
    
    if not preset or preset not in presets:
        await ctx.send(f'🎛️ Available presets: {", ".join(presets.keys())}')
        return
    
    await vc.set_filter(wavelink.Filter(equalizer=wavelink.Equalizer(levels=presets[preset])))
    await ctx.send(f'✅ Equalizer set to **{preset}**')

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not set!')
        exit(1)
    bot.run(token)
