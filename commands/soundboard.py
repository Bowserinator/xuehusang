import discord
import asyncio
import glob

from fuzzysearch import find_near_matches

from src.logger import logger
from src.command import Command, Event
from src.common import *

audio_files = glob.glob('audio/*')
currently_playing_sound = None


async def play_audio(guild, channel, file):
    global currently_playing_sound
    vc = await get_vc(guild, channel)
    if currently_playing_sound:
        vc.stop_playing()
    currently_playing_sound = True
    vc.play(discord.FFmpegPCMAudio(file))

    while vc.is_playing():
        await asyncio.sleep(1)

    vc.stop_playing()
    currently_playing_sound = False

# ---- Commands -----------

async def play_func(client, message, args):
    if not len(args):
        await send_error_embed(message, f'`Usage: !play <name>`. Use `!listsounds` to get a list of sound names.')
        return

    if message.author.voice:
        # Find closest file
        names = [name.split('/')[-1].split('.')[0] for name in audio_files]
        file_to_play = None

        if args in names:
            file_to_play = audio_files[names.index(args)]
        if not file_to_play:
            def simplify(s):
                return s.lower().replace('_', '').replace('-', '').replace(' ', '')

            matches = [(name, find_near_matches(simplify(args), simplify(names[i]), max_l_dist=4)) for i, name in enumerate(audio_files)]
            best_match_dist = 99999999999
            for match in [m for m in matches if len(m[1])]:
                best_match = min(match[1], key=lambda x: x.dist)
                if best_match.dist < best_match_dist and len(best_match.matched):
                    best_match_dist = best_match.dist
                    file_to_play = match[0]

        if not file_to_play:
            await send_error_embed(message, f'Unknown sound: `{args}`')
            return

        await play_audio(message.guild, message.author.voice.channel, file_to_play)
    else:
        await send_error_embed(message, 'You are not in a voice channel :(')

async def die(client, message, args):
    global currently_playing_sound
    vc = message.guild.voice_client
    if vc:
        vc.stop()
        currently_playing_sound = False
        await vc.disconnect()

async def list_sounds(client, message, args):
    names = [f.split('/')[-1].split('.')[0] for f in audio_files]
    table = ''
    trim = lambda s: s if len(s) <= 20 else s[:18] + '..'

    for i in range(0, len(names), 3):
        n2 = names[i + 1] if i + 1 < len(names) else ""
        n3 = names[i + 2] if i + 2 < len(names) else ""
        table += '{:<20} {:<20} {:<20}\n'.format(trim(names[i]), trim(n2), trim(n3))

    await message.reply(f'```{table}```', mention_author=True)

async def on_user_join_vc(member, before, after):
    if member.id == 293708811435507712: # Play you're an idiot when demo joins vc
        await play_audio(member.guild, after.channel, "audio/youre_an_idiot.wav")

async def leave_vc_if_empty(member, before, after):
    vc = member.guild.voice_client
    if vc is None or before.channel.id != vc.channel.id:
        return
    if len(vc.channel.members) == 1:
        await vc.disconnect() # Leave if last

def add_commands(commands, client, events):
    commands.append(Command(['play', 'p'], play_func, help="`p <sound name>` - Play soundboard sound"))
    commands.append(Command(['listsounds', 'lp', 'listplay'], list_sounds, help="`lp` - List sounds in soundboard"))
    commands.append(Command(['dc', 'die', 'fuckoff'], die, help="`die` - Leave current vc in guild"))

    events[Event.USER_JOINED_VC].append(on_user_join_vc)
    events[Event.USER_LEFT_VC].append(leave_vc_if_empty)
