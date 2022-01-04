#!/usr/bin/env python3

# @authour: Marcin Ryżewski 
# @relase: 04/12/2021

import os
import asyncio
from typing import Set
from datetime import datetime
from dotenv import load_dotenv
from difflib import get_close_matches

import discord
from discord.ext.commands.core import check
from discord.gateway import DiscordClientWebSocketResponse
from discord.ext import commands
from discord.utils import sleep_until
from dotenv.main import dotenv_values
from config import COGS_FLODER, PREFIX_HOST


class HostedBot(commands.Bot):
  def __init__(self, local = "local", **options):
    super().__init__(**options)
    self.local = "local"
    self.run_time = datetime.now()
  
  async def process_commands(self, message):
    if message.author.bot:
      return
    
    ctx = await self.get_context(message)

    if ctx.prefix is None:
      return

    if ctx.command is None and (matches := get_close_matches(message.content, self.all_commands, 1)):
      match, = matches
      bot_msg = await ctx.send(f'Did you mean `{match}`?')

      emojis = ('✅', '❌')

      for emoji in emojis:
        self.loop.create_task(bot_msg.add_reaction(emoji))

        try:
          reaction, _ = await self.wait_for(
            'reaction_add',
            check=lambda r, user: r.message == bot_msg and user == ctx.author and str(r.emoji) in emojis,
            timeout=10)

        except asyncio.TimeoutError:
          return

        finally:
          await bot_msg.delete()

        if str(reaction.emoji) == '❌':
          return

        ctx.command = self.all_commands[match]

    await self.invoke(ctx)


class Setup(commands.Cog):
  """Setup class here you can add some castom 
  configuration about Cog"""
  pass
    

def load_command(bot):
  for file in os.scandir(COGS_FLODER):
    name, ext = os.path.splitext(file.name)

    if ext == ".py":
      bot.load_extension(f"{COGS_FLODER}.{name}")
      

def main():
  load_dotenv()
  env = dotenv_values(".env")

  bot = HostedBot(command_prefix=PREFIX_HOST)
  load_command(bot)
  bot.run(env['TOKEN'])
  
if __name__ == "__main__":
  main()