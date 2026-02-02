import discord
from discord.ext import commands
import asyncio
import yt_dlp
from collections import deque
import random

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!m', intents=intents)

# yt-dlp options
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extract_flat': False,
    'age_limit': 99,
    'geo_bypass': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn',
    'executable': 'F:/bot/Discord bot/ffmpeg.exe'
}

# Music queue per guild
queues = {}

class Song:
    def __init__(self, title, url, duration, requester, search_query):
        self.title = title
        self.url = url
        self.duration = duration
        self.requester = requester
        self.search_query = search_query

class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.loop = False
        self.volume = 0.5

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = MusicQueue()
    return queues[guild_id]

def search_song_sync(query):
    """Search for a song and return its info"""
    print(f"Searching for: {query}")
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            if not query.startswith('http'):
                search_query = f'ytsearch:{query}'
            else:
                search_query = query
            
            print(f"yt-dlp query: {search_query}")
            info = ydl.extract_info(search_query, download=False)
            print(f"yt-dlp returned info: {info is not None}")
            
            if info is None:
                print("Info is None!")
                return None
            
            if 'entries' in info:
                if len(info['entries']) == 0:
                    print("No entries found!")
                    return None
                info = info['entries'][0]
            
            print(f"Found: {info.get('title', 'Unknown')}")
            print(f"URL: {info.get('url', 'No URL')[:50] if info.get('url') else 'No URL'}...")
            
            return {
                'source_url': info['url'],
                'title': info.get('title', 'Unknown'),
                'url': info.get('webpage_url', query),
                'duration': info.get('duration', 0)
            }
        except Exception as e:
            print(f"Error searching: {e}")
            import traceback
            traceback.print_exc()
            return None

async def search_song(query):
    """Search for a song asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, search_song_sync, query)

async def get_fresh_audio_url(query):
    """Get a fresh audio URL right before playing"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, search_song_sync, query)
    if result:
        return result['source_url']
    return None

def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS"""
    if not seconds:
        return "Unknown"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

async def play_next(guild, text_channel):
    """Play the next song in the queue"""
    music_queue = get_queue(guild.id)
    
    if not guild.voice_client:
        print("No voice client!")
        return
    
    # If not looping, get next song from queue (only if current is None)
    if not music_queue.loop or music_queue.current is None:
        if music_queue.current is None:
            if len(music_queue.queue) > 0:
                music_queue.current = music_queue.queue.popleft()
            else:
                await text_channel.send("🎵 Queue finished! Add more songs with `!mplay`")
                return
    
    song = music_queue.current
    print(f"About to play: {song.title}")
    
    try:
        print(f"Getting fresh URL for: {song.search_query}")
        fresh_url = await get_fresh_audio_url(song.search_query)
        
        if not fresh_url:
            await text_channel.send(f"❌ Could not get audio for **{song.title}**")
            await play_next(guild, text_channel)
            return
        
        print(f"Got URL: {fresh_url[:100]}...")
        print(f"Creating FFmpeg source...")
        
        source = discord.FFmpegPCMAudio(fresh_url, **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(source, volume=music_queue.volume)
        
        def after_playing(error):
            if error:
                print(f"Player error: {error}")
            else:
                print("Song finished playing normally")
            # Clear current song if not looping
            if not music_queue.loop:
                music_queue.current = None
            asyncio.run_coroutine_threadsafe(play_next(guild, text_channel), bot.loop)
        
        print(f"Starting playback...")
        guild.voice_client.play(source, after=after_playing)
        print(f"Playback started! is_playing: {guild.voice_client.is_playing()}")
        
        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"[{song.title}]({song.url})",
            color=discord.Color.green()
        )
        embed.add_field(name="Duration", value=format_duration(song.duration), inline=True)
        embed.add_field(name="Requested by", value=song.requester.mention, inline=True)
        
        await text_channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error playing: {e}")
        await text_channel.send(f"❌ Error playing song: {e}")
        await play_next(guild, text_channel)

@bot.event
async def on_ready():
    print(f'🎵 {bot.user} is online and ready to play music!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!mplay"))

@bot.event
async def on_message(message):
    print(f"Message received: {message.content}")
    await bot.process_commands(message)

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query: str):
    """Play a song from YouTube"""
    print(f"Play command triggered with query: {query}")
    if not ctx.author.voice:
        return await ctx.send("❌ You need to be in a voice channel!")
    
    voice_channel = ctx.author.voice.channel
    
    if not ctx.voice_client:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)
    
    await ctx.send(f"🔍 Searching for: **{query}**")
    
    song_info = await search_song(query)
    
    if not song_info:
        return await ctx.send("❌ Could not find the song!")
    
    song = Song(
        title=song_info['title'],
        url=song_info['url'],
        duration=song_info['duration'],
        requester=ctx.author,
        search_query=query
    )
    
    music_queue = get_queue(ctx.guild.id)
    
    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        music_queue.queue.append(song)
        embed = discord.Embed(
            title="📝 Added to Queue",
            description=f"[{song.title}]({song.url})",
            color=discord.Color.blue()
        )
        embed.add_field(name="Duration", value=format_duration(song.duration), inline=True)
        embed.add_field(name="Position", value=len(music_queue.queue), inline=True)
        await ctx.send(embed=embed)
    else:
        music_queue.current = song
        await play_next(ctx.guild, ctx.channel)

@bot.command(name='pause')
async def pause(ctx):
    """Pause the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused")
    else:
        await ctx.send("❌ Nothing is playing!")

@bot.command(name='resume', aliases=['unpause'])
async def resume(ctx):
    """Resume the paused song"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed")
    else:
        await ctx.send("❌ Nothing is paused!")

@bot.command(name='skip', aliases=['s', 'next'])
async def skip(ctx):
    """Skip the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped")
    else:
        await ctx.send("❌ Nothing is playing!")

@bot.command(name='stop', aliases=['disconnect', 'dc', 'leave'])
async def stop(ctx):
    """Stop playing and disconnect"""
    music_queue = get_queue(ctx.guild.id)
    music_queue.queue.clear()
    music_queue.current = None
    
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected")
    else:
        await ctx.send("❌ Not connected to a voice channel!")

@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    """Show the current queue"""
    music_queue = get_queue(ctx.guild.id)
    
    if not music_queue.current and len(music_queue.queue) == 0:
        return await ctx.send("📭 Queue is empty!")
    
    embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.purple())
    
    if music_queue.current:
        embed.add_field(
            name="Now Playing",
            value=f"[{music_queue.current.title}]({music_queue.current.url}) | `{format_duration(music_queue.current.duration)}`",
            inline=False
        )
    
    if len(music_queue.queue) > 0:
        queue_list = ""
        for i, song in enumerate(list(music_queue.queue)[:10], 1):
            queue_list += f"`{i}.` [{song.title}]({song.url}) | `{format_duration(song.duration)}`\n"
        
        if len(music_queue.queue) > 10:
            queue_list += f"\n*... and {len(music_queue.queue) - 10} more*"
        
        embed.add_field(name="Up Next", value=queue_list, inline=False)
    
    embed.set_footer(text=f"Total songs in queue: {len(music_queue.queue)}")
    await ctx.send(embed=embed)

@bot.command(name='np', aliases=['nowplaying', 'current'])
async def nowplaying(ctx):
    """Show the currently playing song"""
    music_queue = get_queue(ctx.guild.id)
    
    if not music_queue.current:
        return await ctx.send("❌ Nothing is playing!")
    
    song = music_queue.current
    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"[{song.title}]({song.url})",
        color=discord.Color.green()
    )
    embed.add_field(name="Duration", value=format_duration(song.duration), inline=True)
    embed.add_field(name="Requested by", value=song.requester.mention, inline=True)
    embed.add_field(name="Loop", value="✅ On" if music_queue.loop else "❌ Off", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='vol', aliases=['volume', 'v'])
async def volume(ctx, vol: int = None):
    """Set the volume (0-100)"""
    music_queue = get_queue(ctx.guild.id)
    
    if vol is None:
        return await ctx.send(f"🔊 Current volume: **{int(music_queue.volume * 100)}%**")
    
    if not 0 <= vol <= 100:
        return await ctx.send("❌ Volume must be between 0 and 100!")
    
    music_queue.volume = vol / 100
    
    if ctx.voice_client and ctx.voice_client.source:
        ctx.voice_client.source.volume = music_queue.volume
    
    await ctx.send(f"🔊 Volume set to **{vol}%**")

@bot.command(name='loop', aliases=['repeat'])
async def loop(ctx):
    """Toggle loop for the current song"""
    music_queue = get_queue(ctx.guild.id)
    music_queue.loop = not music_queue.loop
    
    if music_queue.loop:
        await ctx.send("🔁 Loop **enabled**")
    else:
        await ctx.send("🔁 Loop **disabled**")

@bot.command(name='clear')
async def clear(ctx):
    """Clear the queue"""
    music_queue = get_queue(ctx.guild.id)
    music_queue.queue.clear()
    await ctx.send("🗑️ Queue cleared!")

@bot.command(name='shuffle')
async def shuffle(ctx):
    """Shuffle the queue"""
    music_queue = get_queue(ctx.guild.id)
    
    if len(music_queue.queue) < 2:
        return await ctx.send("❌ Need at least 2 songs in queue to shuffle!")
    
    queue_list = list(music_queue.queue)
    random.shuffle(queue_list)
    music_queue.queue = deque(queue_list)
    
    await ctx.send("🔀 Queue shuffled!")

@bot.command(name='remove')
async def remove(ctx, position: int):
    """Remove a song from the queue by position"""
    music_queue = get_queue(ctx.guild.id)
    
    if position < 1 or position > len(music_queue.queue):
        return await ctx.send(f"❌ Invalid position! Use 1-{len(music_queue.queue)}")
    
    queue_list = list(music_queue.queue)
    removed = queue_list.pop(position - 1)
    music_queue.queue = deque(queue_list)
    
    await ctx.send(f"🗑️ Removed **{removed.title}** from the queue")

@bot.command(name='commands', aliases=['h'])
async def help_music(ctx):
    """Show all music commands"""
    embed = discord.Embed(title="🎵 Music Bot Commands", color=discord.Color.blue())
    
    commands_list = """
    `!mplay <song>` - Play a song (YouTube URL or search)
    `!mpause` - Pause the current song
    `!mresume` - Resume playback
    `!mskip` - Skip to the next song
    `!mstop` - Stop and disconnect
    `!mqueue` - Show the queue
    `!mnp` - Show current song
    `!mvol <0-100>` - Set volume
    `!mloop` - Toggle song loop
    `!mshuffle` - Shuffle the queue
    `!mclear` - Clear the queue
    `!mremove <position>` - Remove song from queue
    """
    
    embed.description = commands_list
    embed.set_footer(text="Aliases: !mp, !ms, !mq, !mdc")
    
    await ctx.send(embed=embed)

# Run the bot
bot.run('MTQ2MzYxMzg1MTQ5MTc2MjI0OQ.G2bisz.QwR2qkli5-9iMZKh1LNYcjz2k17-zNKXdPzwEs')
