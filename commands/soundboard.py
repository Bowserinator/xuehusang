import discord
import asyncio
import glob

from fuzzysearch import find_near_matches

from src.logger import logger
from src.command import Command

audio_files = glob.glob('audio/*')
vc = None # TODO global bot state
currently_playing_sound = None

async def play_func(client, message, args):
    if not len(args):
        await message.reply(f'`Usage: !play <name>`. Use `!listsounds` to get a list of sound names.', mention_author=True)
        return

    if message.author.voice:
        # Find closest file
        names = [name.split('/')[-1].split('.')[0] for name in audio_files]
        file_to_play = None

        if args in names:
            file_to_play = audio_files[names.index(args)]
        if not file_to_play:
            matches = [(name, find_near_matches(args.lower(), names[i].lower(), max_l_dist=8)) for i, name in enumerate(audio_files)]
            best_match_dist = 99999999999
            for match in [m for m in matches if len(m[1])]:
                best_match = min(match[1], key=lambda x: x.dist)
                if best_match.dist < best_match_dist and len(best_match.matched):
                    best_match_dist = best_match.dist
                    file_to_play = match[0]

        if not file_to_play:
            await message.reply(f'Unknown sound: `{args}`', mention_author=True)
            return

        channel = message.author.voice.channel
        global vc, currently_playing_sound
        if not vc:
            vc = await channel.connect()

        if currently_playing_sound:
            vc.stop()
        currently_playing_sound = True
        vc.play(discord.FFmpegPCMAudio(file_to_play))

        while vc.is_playing():
            await asyncio.sleep(1)

        vc.stop()
        currently_playing_sound = False
        # await vc.disconnect()
    else:
        await message.reply('You are not in a voice channel :(', mention_author=True)


async def list_sounds(client, message, args):
    names = [f.split('/')[-1].split('.')[0] for f in audio_files]
    table = ''
    trim = lambda s: s if len(s) <= 20 else s[:18] + '..'

    for i in range(0, len(names), 3):
        n2 = names[i + 1] if i + 1 < len(names) else ""
        n3 = names[i + 2] if i + 2 < len(names) else ""
        table += '{:<20} {:<20} {:<20}\n'.format(trim(names[i]), trim(n2), trim(n3))

    await message.reply(f'```{table}```', mention_author=True)


def add_commands(commands, client):
    commands.append(Command(['play', 'p'], play_func, help="Play soundboard sound"))
    commands.append(Command(['listsounds', 'lp', 'listplay'], list_sounds, help="List sounds in soundboard"))
