import discord
from discord.ext import commands
import edge_tts
import asyncio
import os

# Bot setup with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# TTS settings
TTS_VOICE = "en-US-GuyNeural"  # You can change this voice
TEMP_AUDIO_FILE = "tts_output.mp3"


@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready!')
    print(f'Connected to {len(bot.guilds)} server(s)')


@bot.command(name='join')
async def join(ctx):
    """Join the user's voice channel"""
    if ctx.author.voice is None:
        await ctx.send("❌ You need to be in a voice channel!")
        return
    
    channel = ctx.author.voice.channel
    
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    
    await ctx.send(f"✅ Joined **{channel.name}**")


@bot.command(name='leave')
async def leave(ctx):
    """Leave the voice channel"""
    if ctx.voice_client is None:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    await ctx.voice_client.disconnect()
    await ctx.send("👋 Left the voice channel")


@bot.command(name='say')
async def say(ctx, *, message: str):
    """Convert text to speech and play it in voice channel"""
    if ctx.voice_client is None:
        # Auto-join if not in a channel
        if ctx.author.voice is None:
            await ctx.send("❌ You need to be in a voice channel, or use `!join` first!")
            return
        await ctx.author.voice.channel.connect()
    
    # Check if already playing audio
    if ctx.voice_client.is_playing():
        await ctx.send("⏳ Please wait, I'm still speaking...")
        return
    
    try:
        # Generate TTS audio using edge-tts
        communicate = edge_tts.Communicate(message, TTS_VOICE)
        await communicate.save(TEMP_AUDIO_FILE)
        
        # Play the audio
        audio_source = discord.FFmpegPCMAudio(TEMP_AUDIO_FILE)
        ctx.voice_client.play(audio_source)
        
        await ctx.send(f"🔊 Speaking: *{message}*")
        
        # Wait for audio to finish, then clean up
        while ctx.voice_client and ctx.voice_client.is_playing():
            await asyncio.sleep(0.5)
        
        # Clean up temp file
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name='stop')
async def stop(ctx):
    """Stop the current TTS playback"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped speaking")
    else:
        await ctx.send("❌ Nothing is playing right now")


@bot.command(name='voice')
async def set_voice(ctx, *, voice_name: str):
    """Change the TTS voice"""
    global TTS_VOICE
    TTS_VOICE = voice_name
    await ctx.send(f"✅ Voice changed to: **{voice_name}**")


@bot.command(name='voices')
async def list_voices(ctx):
    """List some available TTS voices"""
    voices = """
**Available Voices (examples):**
🇺🇸 `en-US-GuyNeural` - US Male
🇺🇸 `en-US-JennyNeural` - US Female
🇬🇧 `en-GB-RyanNeural` - UK Male
🇬🇧 `en-GB-SoniaNeural` - UK Female
🇦🇺 `en-AU-WilliamNeural` - Australian Male
🇮🇳 `en-IN-NeerjaNeural` - Indian Female

Use `!voice <voice_name>` to change voice
    """
    await ctx.send(voices)


@bot.command(name='ttshelp')
async def tts_help(ctx):
    """Show help for TTS bot commands"""
    help_text = """
**🔊 TTS Bot Commands:**

`!join` - Join your voice channel
`!leave` - Leave the voice channel
`!say <message>` - Speak a message in voice chat
`!stop` - Stop current speech
`!voice <name>` - Change TTS voice
`!voices` - List available voices
`!ttshelp` - Show this help message
    """
    await ctx.send(help_text)


# Run the bot - Replace with your token!
if __name__ == "__main__":
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # ⚠️ Replace with your actual bot token
    bot.run(TOKEN)
