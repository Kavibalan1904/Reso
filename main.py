import discord
from discord.ext import commands
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
    print(f'✅ {bot.user} is online!')
    print(f'Connected to {len(bot.guilds)} servers')
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="!join to start"))

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
            # Try to connect with timeout
            await channel.connect(timeout=10.0, reconnect=True, self_deaf=True)
        
        await ctx.send(f'✅ Connected to **{channel.name}**')
        
        # Test if voice is working
        await asyncio.sleep(2)
        if ctx.voice_client and ctx.voice_client.is_connected():
            await ctx.send('🔊 Voice connection established! Try `!play test`')
        else:
            await ctx.send('⚠️ Voice connection may be unstable')
            
    except asyncio.TimeoutError:
        await ctx.send('❌ Connection timed out. Please try again.')
    except discord.Forbidden:
        await ctx.send('❌ I don\'t have permission to join that voice channel!')
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)[:100]}')

@bot.command(name='play')
async def play(ctx, *, song):
    """Test play command"""
    if not ctx.voice_client:
        await ctx.invoke(join)
        await asyncio.sleep(2)
    
    if ctx.voice_client:
        await ctx.send('🎵 Bot is ready to play music!')
        await ctx.send('⚠️ Note: YouTube playback requires additional setup.')
        await ctx.send('💡 Try using a direct MP3 URL or SoundCloud link')
    else:
        await ctx.send('❌ Bot is not in a voice channel')

@bot.command(name='leave')
async def leave(ctx):
    """Bot leaves voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('👋 Left voice channel')
    else:
        await ctx.send('❌ I\'m not in a voice channel!')

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f'🏓 Pong! `{round(bot.latency * 1000)}ms`')

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not set!')
        exit(1)
    
    print('Starting bot...')
    bot.run(token)
