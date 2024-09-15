import modules.calc.parse as parse
import modules.calc.format as format

from src.logger import logger
from src.command import Command, Event
from src.common import *

from modules.butil import Timeout

async def calc_func(client, message, args):
    try:
        table = '<timed out>'
        with Timeout(seconds=1):
            table = format.format(parse.calc(args))
    except Exception as e:
        table = str(e)
    await message.reply(f'```{table}```', mention_author=True)

def add_commands(commands, client, events):
    commands.append(Command(['calc'], calc_func, help="`calc <expr>` - Calculator thats better than that piece of shit yuuka"))
