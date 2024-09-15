import discord
from discord.ext import voice_recv
import asyncio

from modules.butil import CyclicWave

BOT_COLOR = 0xbae2ff

async def send_error_embed(message, error_msg, mention_author=True):
    embed = discord.Embed(color=0xFF0000)
    embed.add_field(name='Error', value=error_msg, inline=True)
    await message.reply(embed=embed, mention_author= mention_author)

async def send_msg_embed(message, msg, mention_author=True):
    embed = discord.Embed(description=msg, color=BOT_COLOR)
    await message.reply(embed=embed, mention_author= mention_author)

async def get_vc(guild, target_channel):
    """
    Get voice client obj for target_channel (voice channel),
    joining the channel if not already in it
    """
    vc = guild.voice_client
    if vc is not None and vc.channel.id != target_channel.id:
        vc.stop_listening()
        await vc.disconnect()
        vc = None
    if vc is None:
        vc = await target_channel.connect(cls=voice_recv.VoiceRecvClient)

        # TODO
        # global sink
        # sink = voice_recv.WaveSink(CyclicWave('test.wav'))
        # vc.listen(sink, after=lambda e: print('DONE!!'))
    return vc
