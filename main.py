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
async def hello(ctx):
    await ctx.send("Choo choo! 🚅")


@client.command()
async def play(ctx, *, query): 

    def playQueue(ctx, voice):

        print("almaaaa")

        if len(queue) == 0:
            pass

        else:

            # Searches for query on YouTube
            print(f"Searching for: {queue[0]}")
            search = Search(queue[0], limit = 1)
            url = "https://www.youtube.com/watch?v=" + search.result()['result'][0]["id"]
            print(f"Found the following url: {url}")

            # Gets the highest bitrate audio stream with pafy
            ydl_opts = {'format': 'm4a/bestaudio/best'}
            play_url = None
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                play_url = ydl.sanitize_info(info)["url"]

            try:
                voice.play(discord.FFmpegOpusAudio(play_url), after = lambda e: playQueue(ctx = ctx, voice = voice))

                queue.pop(0)
                
                coro = ctx.send(f"Playing from **queue**: {url}")
                fut = asyncio.run_coroutine_threadsafe(coro, client.loop)

                try:
                    fut.result()
                except:
                    # an error happened sending the message
                    pass

                if len(queue) > 0:
                    coro = ctx.send(f"Next: {queue[0]}")
                    fut = asyncio.run_coroutine_threadsafe(coro, client.loop)

                    try:
                        fut.result()

                    except:
                        pass


                history = open(str(ctx.guild.id), 'a')
                history.write(url + datetime.now().strftime(" %Y.%m.%d - %H:%M") + f", Requested by: {ctx.author.name}\n")
                history.close()

            except ClientException:
                pass


    # Connects to a voice channel
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name = ctx.guild.voice_channels[0].name)

    try:
        await voice_channel.connect()

    except:
        pass

    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

    if voice.is_playing():
        queue.append(query)
        await ctx.send(f"Queued {query}")

    else:
        # Searches for query on YouTube
        print(f"Searching for: {query}")
        search = Search(query, limit = 1)
        url = "https://www.youtube.com/watch?v=" + search.result()['result'][0]["id"]
        print(f"Found the following url: {url}")

        # Gets the highest bitrate audio stream with pafy
        ydl_opts = {'format': 'm4a/bestaudio/best'}
        play_url = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            play_url = ydl.sanitize_info(info)["url"]



        voice.play(discord.FFmpegOpusAudio(play_url), after = lambda e: playQueue(ctx = ctx, voice = voice))
            
        await ctx.send(f"Playing: {url}")

        if len(queue) > 0:
            await ctx.send(f"Next: {queue[0]}")

        history = open(str(ctx.guild.id), 'a')
        history.write(url + datetime.now().strftime(" %Y.%m.%d - %H:%M") + f", Requested by: {ctx.author.name}\n")
        history.close()




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


@client.command()
async def history(ctx):
    await ctx.send("Play history:")

    history = open(str(ctx.guild.id), 'r')

    for line in history:
        await ctx.send(line)

    history.close()


@client.command()
async def clearhistory(ctx):
    await ctx.send("Clearing history...")

    history = open(str(ctx.guild.id), 'w')
    history.write("")
    history.close()

    await ctx.send("Done.")


@client.command()
async def clearqueue(ctx, entry = "all"):
    if entry == "all":
        queue.clear()
        await ctx.send("Queue cleared")

    else:
        temp = str(queue[int(entry) - 1])
        queue.pop(int(entry) - 1)
        await ctx.send(f"Removed {temp} from queue.")

@client.command()
async def showqueue(ctx):
    await ctx.send("Queue:")
    for i in range(len(queue)):
        await ctx.send(f"{i + 1}.: {queue[i]}")





client.run(os.environ["DISCORD_TOKEN"])

