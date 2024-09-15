import discord
from src.logger import logger
from src.command import Command, Event
from src.common import *

global cmds

async def help_func(client, message, args):
    if not len(args):
        await send_error_embed(message, f'Use `!help` to get help for a command or `!list` to list all commands')
        return
    for cmd in cmds:
        if args in cmd.names:
            embed = discord.Embed(description=cmd.help, color=BOT_COLOR)
            if len(cmd.names) > 1:
                embed.add_field(name="Aliases", value='`' + ', '.join(cmd.names) + '`', inline=True)
            await message.reply(embed=embed)
            return
    await send_error_embed(message, f'Unknown command: `{args}`')

async def list_func(client, message, args):
    out = ''
    for i, cmd in enumerate(sorted(cmds, key=lambda x: x.names[0])):
        out += cmd.names[0].ljust(15) + ' '
        if i % 3 == 2:
            out += '\n'
    out = f'```{out}```'
    embed = discord.Embed(color=BOT_COLOR)
    embed.add_field(name='Commands', value=out, inline=True)
    await message.reply(embed=embed, mention_author=True)

def add_commands(commands, client, events):
    global cmds
    cmds = commands
    commands.append(Command(['h', 'help'], help_func, help="`help <command name>` - Get help message for command"))
    commands.append(Command(['l', 'list'], list_func, help="`list` - List commands you can use"))
