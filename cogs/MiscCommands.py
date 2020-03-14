import discord
import requests
import time
from datetime import datetime
from discord.ext import commands

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Bot ping")
    @commands.guild_only()
    async def ping(self, ctx):
        # make a request to discord status page to get latest api ping
        response = requests.get("https://discord.statuspage.io/metrics-display/ztt4777v23lf/day.json").json()
        latest_ping = response["summary"]["last"]
        # gets the time (as of the message being sent)
        before = time.monotonic()
        # sends a message to the channel
        message = await ctx.send("Pong!")
        # calculates the ping using the current time and the time the message was sent
        ping = (time.monotonic() - before) * 1000
        # creates a new embed, sets title to blank with a description and color (color int generator: https://www.shodor.org/stella2java/rgbint.html)
        embed = discord.Embed(title="Bot Response Time", description=None, color=discord.Colour.green(),
                              timestamp=datetime.utcnow())
        # adds a new field to the embed
        embed.add_field(name="🤖 Bot Latency", value=f"{int(ping)}ms", inline=True)
        embed.add_field(name="🌐 API Latency", value=f"{round(self.bot.latency, 2)}ms", inline=True)
        embed.add_field(name="Latest API Ping", value=f"{latest_ping}ms")
        # adds a footer to the embed with the bot name and avatar
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        # edits the previous message sent with the new embed
        await message.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(MiscCommands(bot))
