import requests
from requests.utils import requote_uri
import random

from src.logger import logger
from src.command import Command, Event
from src.common import *


async def get_mal(client, message, args):
    url = 'https://myanimelist.net/search/prefix.json?type=all&v=1&keyword=' + requote_uri(args)
    res = requests.get(url)
    if res.status_code != 200:
        await send_error_embed(message, f'Failed to get API res code {res.status_code}')
        return
    json = res.json()
   
    def format_item(item):
        meta = item['payload']
        extra = ''
        if 'score' in meta:
            if 'one piece' in item['name'].lower():
                meta['score'] = 1
            extra = f'\n-# (score= {meta.get("score", "?")}, year= {meta.get("start_year", "?")})'
        return f'[{item["name"]}](<{item["url"]}>){extra}\n'

    embed = discord.Embed(color=BOT_COLOR)
    outs = {}
    categories = []

    for category in json['categories']:
        items = category['items'][:3]
        items.sort(key=lambda x: x['es_score'], reverse=True)
        categories.append(category['type'])
        outs[category['type']] =  ''.join([format_item(i) for i in items])

    for category in categories:
        embed.add_field(name=category.title(), value=outs[category], inline=False)
    await message.reply(embed=embed, mention_author=True)


async def get_art(client, message, args):
    # https://hellomouse.net/fluff/fluff/fluff-0016.jpg
    exts = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'avif', 'mp4']
    fid = str(random.randint(1, 4085)).zfill(4)
    for ext in exts:
        url = f'https://hellomouse.net/fluff/fluff/fluff-{fid}.{ext}'
        if requests.get(url).status_code == 200:
            embed = discord.Embed(description = f'-# Fluff id {fid}', color = BOT_COLOR)
            embed.set_image(url = url)
            await message.channel.send(embed=embed)
            return
    await send_error_embed(message, f'Failed to get fluff :(')


def add_commands(commands, client, events):
    commands.append(Command(['mal'], get_mal, help="`get_mal <search>` - Search for anime on mal"))
    commands.append(Command(['art'], get_art, help="`art` - Get random art from old hellomouse fluff archive v1"))
