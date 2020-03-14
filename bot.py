import discord
import os
from discord.ext import commands
from discord.ext.commands import errors
from dotenv import load_dotenv

from Utils import SetupLogger, getLogger

load_dotenv()

PREFIX = "corona "
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix=PREFIX, description="CoronaBot", case_insensitive=True, owner_id=213247101314924545)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(name="with infectious diseases!", type=discord.ActivityType.playing))
    loadCogs()


def loadCogs():
    for cog in os.listdir("cogs"):
        if cog.endswith("py"):
            filename = cog.split(".")[0]
            try:
                bot.load_extension(f"cogs.{filename}")
                getLogger().info(f"[Cog Management] Cog Loaded: {filename}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                getLogger().error(f"[Cog Management] Error loading cog: {filename}; Error: {e}")


if __name__ == "__main__":
    # setup the logger with colored logger and verbose logging
    SetupLogger(full_debug=False)

bot.run(TOKEN)
