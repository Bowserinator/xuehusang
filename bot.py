import os, glob
import collections
from dotenv import load_dotenv

import discord
import asyncio

from src.logger import logger as logging
from src.command import Event

# Construct bot
# -----------------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)

COMMAND_CHAR = '!'

# Import commands
# -----------------------------
commands = []
name2cmd = {}
events = collections.defaultdict(lambda: [])

for file in glob.glob('commands/*.py'):
    file = file.split('/')[1].replace('.py', '')
    if file == "__init__":
        continue
    
    command_module = __import__(f'commands.{file}')
    module = getattr(command_module, file)
    if 'add_commands' not in dir(module):
        raise RuntimeError(f'Missing add_commands() function in command file {file}')

    module.add_commands(commands, client, events)

for command in commands:
    for alias in command.names:
        if alias in name2cmd:
            logging.warning(f'Conflicting alias for alias "{alias}"!')
        name2cmd[alias] = command


@client.event
async def on_ready():
    logging.info(f'{client.user} is connected to the following guilds:')
    for guild in client.guilds:
        logging.info(f'- {guild.name}(id: {guild.id})')

    activity = discord.Game(name="Blue Archive")
    await client.change_presence(status=discord.Status.idle, activity=activity)

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel:
        for event in events[Event.USER_JOINED_VC]:
            await event(member, before, after)
    elif before.channel and after.channel is None:
        for event in events[Event.USER_LEFT_VC]:
            await event(member, before, after)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    logging.info(f'{message.author.name}: {message.content}')
    if message.content.startswith(COMMAND_CHAR):
        command_text = message.content.split(' ')[0][len(COMMAND_CHAR):]
        if command_text not in name2cmd: return
        command = name2cmd[command_text]

        args = message.content.split(' ', 1)[1].strip() if ' ' in message.content else ''
        await command.func(client, message, args)

client.run(TOKEN)
