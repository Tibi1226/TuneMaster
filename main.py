# TuneMaster
# hihi

import os
import discord
from discord.ext import commands
import asyncio
from discord.ext import commands
from discord.errors import *
from discord.ext.commands.errors import *
from youtubesearchpython import Search
import json
import yt_dlp
from datetime import datetime


intents = discord.Intents.all()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)


queue = []


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    users = 0
    for guild in client.guilds:
        users += guild.member_count
    print(f"Statistics: Guilds:{len(client.guilds)} Users:{users}")
    print(f"Guilds:")
    for guild in client.guilds:
        print(f"{guild.name}: {guild.member_count}")

@client.command()
async def play(ctx, *, query):
    voice_channel = ctx.guild.voice_channels[0]

    try:
        await voice_channel.connect()
    except ClientException:
        print("Line 43 - Already connected to voice channel")

    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {'format': 'm4a/bestaudio/best'}
    play_url = None
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        play_url = ydl.sanitize_info(info)["url"]
        url = "https://www.youtube.com/watch?v=" + str(ydl.sanitize_info(info)["id"])

    try:
        voice_client.play(discord.FFmpegOpusAudio(play_url))
        await ctx.send(f"Playing {url}")


    except ClientException as e:
        await ctx.send(f"Already playing")


@client.command()
async def disconnect(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
    try:
        if voice.is_connected():
            await voice.disconnect()
            await ctx.message.add_reaction("\N{Black Telephone}")
        else:
            await ctx.send("Not connected to any voice channel.")

    except AttributeError:
        await ctx.send("Not connected to any voice channel")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
    try:
        if voice.is_playing():
            await ctx.message.add_reaction("\N{DOUBLE VERTICAL BAR}")
            voice.pause()
        
        else:
            await ctx.send("No music is playing.")


    except AttributeError:
        await ctx.send("No music is playing.")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

    try:
        if voice.is_paused():
            voice.resume()
            await ctx.message.add_reaction("\N{Black Right-Pointing Triangle}")
        
        elif not voice.is_playing():
            await ctx.send("No music is playing.")

        else:
            await ctx.send("The music is already playing")

    except AttributeError:
        await ctx.send("No music is playing.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

    try:
        print("1")
        voice.stop()
        print("2")
        await ctx.message.add_reaction("\N{Black Square for Stop}")

    except AttributeError:
        await ctx.send("No music is playing.")



client.run(os.environ["DISCORD_TOKEN"])

