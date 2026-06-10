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
    
    try:
        node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
        await wavelink.Pool.connect(client=bot, nodes=[node])
        print('✅ Connected to Lavalink')
    except Exception as e:
        print(f'⚠️ Error: {e}')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='join')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send('Join a voice channel first!')
        return
    
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect(self_deaf=True)
    
    await ctx.send(f'Joined {channel.name}')

@bot.command(name='play')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send('Join a voice channel first!')
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(1)
    
    vc = ctx.voice_client
    await ctx.send(f'Searching for: {search}')
    
    try:
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            await ctx.send('No results found!')
            return
        
        track = tracks[0] if isinstance(tracks, list) else tracks
        
        if vc.is_playing():
            await vc.queue.put_wait(track)
            await ctx.send(f'Added to queue: {track.title}')
        else:
            await vc.play(track)
            await ctx.send(f'Now playing: {track.title}')
            await vc.set_volume(100)
            
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')

@bot.command(name='volume')
async def volume(ctx, vol: int):
    if ctx.voice_client:
        await ctx.voice_client.set_volume(vol)
        await ctx.send(f'Volume set to {vol}%')

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Stopped')

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.pause()
        await ctx.send('Paused')

@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        await ctx.voice_client.resume()
        await ctx.send('Resumed')

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.stop()
        await ctx.send('Skipped')

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
