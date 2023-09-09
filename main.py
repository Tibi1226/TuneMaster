# TuneMaster

import os
import discord
from discord.errors import *
from discord.ext import commands
from discord.ext.commands.errors import *
from youtubesearchpython import Search
import yt_dlp
import asyncio

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

queue_list = []


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
    def play_queue(ctx, voice):

        print("almaaaa")

        if len(queue_list) == 0:
            pass

        else:

            # Searches for query on YouTube
            print(f"Searching for: {queue_list[0]}")
            search = Search(queue_list[0], limit=1)
            url = "https://www.youtube.com/watch?v=" + search.result()['result'][0]["id"]
            print(f"Found the following url: {url}")

            # Gets the highest bitrate audio stream with pafy
            ydl_opts = {'format': 'm4a/bestaudio/best'}
            play_url = None
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                play_url = ydl.sanitize_info(info)["url"]

            try:
                voice.play(discord.FFmpegOpusAudio(play_url), after=lambda e: play_queue(ctx=ctx, voice=voice))

                queue_list.pop(0)

                coro = ctx.send(f"Playing from queue: {url}")
                fut = asyncio.run_coroutine_threadsafe(coro, client.loop)

                try:
                    fut.result()
                except:
                    # an error happened sending the message
                    pass

                if len(queue_list) > 0:
                    coro = ctx.send(f"Next: {queue_list[0]}")
                    fut = asyncio.run_coroutine_threadsafe(coro, client.loop)

                    try:
                        fut.result()

                    except:
                        pass

            except ClientException:
                pass

    # Connects to a voice channel
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.guild.voice_channels[0].name)

    try:
        await voice_channel.connect()

    except:
        pass

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        print("voice is playing")
        search = Search(query, limit=1)
        url = "https://www.youtube.com/watch?v=" + search.result()['result'][0]["id"]
        queue_list.append(url)
        await ctx.send(f"Queued {url}")

    else:
        # Searches for query on YouTube
        print(f"Searching for: {query}")
        search = Search(query, limit=1)
        url = "https://www.youtube.com/watch?v=" + search.result()['result'][0]["id"]
        print(f"Found the following url: {url}")

        ydl_opts = {'format': 'm4a/bestaudio/best'}
        play_url = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            play_url = ydl.sanitize_info(info)["url"]

        voice.play(discord.FFmpegOpusAudio(play_url), after=lambda e: play_queue(ctx=ctx, voice=voice))

        await ctx.send(f"Playing: {url}")

        if len(queue_list) > 0:
            await ctx.send(f"Next: {queue_list[0]}")


@client.command()
async def disconnect(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

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
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

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
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

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
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        voice.stop()
        await ctx.message.add_reaction("\N{Black Right-Pointing Double Triangle with Vertical Bar}")

    except AttributeError:
        await ctx.send("No music is playing.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        queue_list.clear()
        voice.stop()
        await ctx.message.add_reaction("\N{Black Square for Stop}")

    except AttributeError:
        await ctx.send("No music is playing.")


@client.command()
async def clear(ctx, entry="all"):
    if entry == "all":
        queue_list.clear()
        await ctx.send("Queue cleared")

    else:
        temp = str(queue_list[int(entry) - 1])
        queue_list.pop(int(entry) - 1)
        await ctx.send(f"Removed {temp}")


@client.command()
async def queue(ctx):
    await ctx.send("Queue:")
    msg = ""
    for i in range(len(queue_list)):
        msg += f"{i + 1}. {queue_list[i]}\n"

    await ctx.send(msg)


client.run(os.environ["DISCORD_TOKEN"])
