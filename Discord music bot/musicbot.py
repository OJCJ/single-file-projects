import discord
import youtube_dl
import os
import re
import urllib.request
import random
import asyncio
from discord.ext import commands
from pytube import YouTube

client = commands.Bot(command_prefix="!")

musicQueue = []
playerLoop = False

def findLink(s):
	regex = r"(https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})"
	url = re.findall(regex,s)
	return [x[1] for x in url]

def youtubeSearch(search):
	html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + "_".join(search))
	video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
	return "https://www.youtube.com/watch?v=" + video_ids[0]

def playSong(ctx, url, l = None): # l -> looped
	voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

	ydl_opts = {"format":"249/250/251"}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])
	for file in os.listdir("./"):
		if file.endswith(".webm") and file != "song.webm":
			if os.path.isfile("song.webm"):
				os.remove("song.webm")
			os.rename(file, "song.webm")
	voice.play(discord.FFmpegPCMAudio("song.webm"), after = lambda e: nextSong(ctx) if not playerLoop else playSong(ctx, musicQueue[0][1],True))

	if not l:
		asyncio.run_coroutine_threadsafe(ctx.send(f"Now playing: {YouTube(url).title}"), client.loop)

def nextSong(ctx):
	del musicQueue[0]
	if len(musicQueue) > 0:
		try:
			playSong(ctx, musicQueue[0][1])
		except:
			pass

@client.command(aliases = ['p'])
async def play(ctx, *query:str):
	if len(findLink(' '.join(query))) > 0:
		for i in query:
			if len(findLink(i)) > 0:
				url = findLink(i)[0]
				break
	else:
		url = youtubeSearch(query)
	
	song_there = os.path.isfile("song.webm")
	musicQueue.append((YouTube(url).title, url))
	try:
		if song_there:
			os.remove("song.webm")
	except PermissionError:
		await ctx.send(f"{YouTube(url).title} added to queue.")
		return

	try:
		voiceChannel = ctx.author.voice.channel
	except AttributeError:
		await ctx.send("You have to be in a voice channel to play music.")
		return

	try:
		await voiceChannel.connect()
	except:
		pass

	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

	if not voice.is_playing():
		playSong(ctx, musicQueue[0][1])

@client.command(aliases = ['disconnect', 'dc'])
async def leave(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_connected():
		musicQueue = []
		await voice.disconnect()
	else:
		await ctx.send("The bot is not connected to any channel.")

@client.command()
async def pause(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_playing():
		voice.pause()
		await ctx.send("Song paused.")
	elif voice.is_paused():
		voice.resume()
		await ctx.send("Song resumed.")
	else: ctx.send("No audio is playing.")

@client.command(aliases = ['continue', 'unpause'])
async def resume(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_paused():
		voice.resume()
		await ctx.send("Song resumed.")
	else: ctx.send("Audio is not paused.")

@client.command()
async def stop(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	musicQueue.clear()
	voice.stop()

@client.command(aliases = ['q', 'songs'])
async def queue(ctx):
	if len(musicQueue) > 0:
		queueString = ""
		for i in range(len(musicQueue)):
			queueString += f"[{i+1}] {musicQueue[i][0]}\n"
		await ctx.send(f"```fix\nQueue:\n> {queueString}```")
	else:
		await ctx.send("No songs in queue.")

@client.command(aliases = ['playing','current','now'])
async def np(ctx):
	if len(musicQueue) > 0:
		await ctx.send(f"Currently playing: {musicQueue[0][0]}.")
	else:
		await ctx.send("No music currently playing.")

@client.command(aliases = ['r'])
async def remove(ctx, index:int):
	if len(musicQueue) > 0:
		title = musicQueue[index-1][0]
		musicQueue.pop(index-1)
		await ctx.send(f"Removed {title} from the queue.")
	else:
		await ctx.send("Can't remove song; queue is empty.")

@client.command()
async def shuffle(ctx):
	if len(musicQueue) > 0:
		tempList = musicQueue[queueCursor:-1]
		random.shuffle(tempList)
		musicQueue = musicQueue[0:queueCursor] + tempList
		await ctx.send("Queue has been shuffled.")
	else:
		await ctx.send("Cannot shuffle, there are no songs in the queue")

@client.command(aliases = ['connect'])
async def join(ctx):
	try:
		voiceChannel = ctx.author.voice.channel
	except AttributeError:
		await ctx.send("You have to be in a voice channel to invite the bot.")
		return

	try:
		await voiceChannel.connect()
	except CommandInvokeError:
		pass

@client.command(aliases = ['l','repeat'])
async def loop(ctx):
	global playerLoop
	playerLoop = not playerLoop
	await ctx.send("Current song looped.") if playerLoop else await ctx.send("Current song unlooped.")

@client.command(aliases = ['c'])
async def clear(ctx):
	global musicQueue
	musicQueue = [musicQueue[0]]
	await ctx.send("Queue cleared.")

@client.command(aliases = ['s', 'fs', 'next','n'])
async def skip(ctx):
	voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if voice.is_playing():
		voice.stop()

	if not voice.is_playing() and len(musicQueue) > 1:
		playSong(ctx, musicQueue[1][1])

@client.command(aliases = ['swap'])
async def move(ctx, i1:int, i2:int):
	if i1 != 1 and i2 != 1:
		musicQueue[i1-1], musicQueue[i2-1] = musicQueue[i2-1], musicQueue[i1-1]
		await ctx.send(f"Song {i1} swapped with song {i2}.")
	else:
		await ctx.send(f"You can't move the current song")


client.run('TOKEN')