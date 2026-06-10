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

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'✅ Reso is online! Logged in as {self.bot.user}')
        print(f'📊 Connected to {len(self.bot.guilds)} servers')
        
        # Setup Lavalink connection
        try:
            node = wavelink.Node(
                uri='http://localhost:2333',
                password='youshallnotpass'
            )
            await wavelink.Pool.connect(client=self.bot, nodes=[node])
            print('✅ Connected to Lavalink')
        except Exception as e:
            print(f'⚠️ Lavalink not ready yet: {e}')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f'🎵 Lavalink node {payload.node.identifier} is ready!')
        
    @commands.command(name='join')
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        await ctx.send(f"✅ Joined {channel.mention}")

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        vc: wavelink.Player = ctx.voice_client
        await ctx.send(f"🔍 Searching for: {query}")
        try:
            tracks = await wavelink.YouTubeTrack.search(query=query, return_first=True)
            if not tracks:
                await ctx.send("❌ No results found!")
                return
            track = tracks[0] if isinstance(tracks, list) else tracks
            if vc.is_playing():
                await vc.queue.put_wait(track)
                await ctx.send(f"📝 Added to queue: **{track.title}**")
            else:
                await vc.play(track)
                await ctx.send(f"🎵 Now playing: **{track.title}**")
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

    @commands.command(name='pause')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            await ctx.voice_client.pause()
            await ctx.send("⏸️ Paused")

    @commands.command(name='resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            await ctx.voice_client.resume()
            await ctx.send("▶️ Resumed")

    @commands.command(name='skip')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            await ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped")

    @commands.command(name='stop')
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("🛑 Stopped")

    @commands.command(name='volume')
    async def set_volume(self, ctx, volume: int):
        if 0 <= volume <= 150:
            if ctx.voice_client:
                await ctx.voice_client.set_volume(volume)
                await ctx.send(f"🔊 Volume set to {volume}%")

    @commands.command(name='eq')
    async def equalizer(self, ctx, preset: str = None):
        if not ctx.voice_client:
            await ctx.send("❌ Bot is not in a voice channel")
            return
        vc: wavelink.Player = ctx.voice_client
        presets = {
            'bass': [(0, 0.2), (1, 0.3), (2, 0.1)],
            'nightcore': [(0, 0.3), (1, 0.2)],
            'classical': [(0, 0.1), (1, -0.1)],
            'pop': [(0, 0.1), (1, 0.1), (2, 0.1)],
            'reset': []
        }
        if not preset or preset not in presets:
            await ctx.send(f"🎛️ Available presets: {', '.join(presets.keys())}")
            return
        await vc.set_filter(wavelink.Filter(equalizer=wavelink.Equalizer(levels=presets[preset])))
        await ctx.send(f"✅ Equalizer set to **{preset}**")

async def setup():
    await bot.add_cog(MusicBot(bot))

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not found! Set it in Railway environment variables.")
        exit(1)
    asyncio.run(setup())
    bot.run(token)
