import json
import logging
import sys
import discord
import os
from discord.ext import commands

with open("./json/config.json", "r") as f:
    config = json.load(f)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=f"{config['additional']['prefix']}",
            intents=discord.Intents.all(),
            application_id=config["additional"]["application_id"],
        )
        self.logger = logging.getLogger(__name__)

    async def setup_hook(self):

        for filename in os.listdir("./rustshopbot/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"rustshopbot.cogs.{filename[:-3]}")
        await bot.tree.sync()

    async def on_ready(self):
        self.logger.info("Bot is ready")


level = logging.INFO
dt_fmt = "%Y-%m-%d %H:%M:%S"
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(level)
formatter = logging.Formatter(
    "{asctime}  {levelname:<8}  {name}: {message}", dt_fmt, style="{"
)

handler.setFormatter(formatter)
root.addHandler(handler)

bot = MyBot()
bot.run(
    config["tokens"]["discord_token"],
    log_handler=handler,
    log_level=level,
    log_formatter=formatter,
    root_logger=root,
)
