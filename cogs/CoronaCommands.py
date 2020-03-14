import asyncio

import discord
from discord.ext import commands
from datetime import datetime

import Utils
from Utils import getLogger, CoronaAPI


class Corona(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_reactions(self, ctx, message, page, pagination, list_type):
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=90.0,
                                                     check=lambda r, u: u == ctx.message.author)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            return await ctx.send(f"Timed out", delete_after=10)
        else:
            if reaction.emoji == "➡":
                page += 1
                new_embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - {list_type} List",
                                          description="\n".join(pagination[page]),
                                          color=discord.Color.orange(),
                                          timestamp=datetime.utcnow())
                new_embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                new_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await message.clear_reactions()
                if page + 1 >= 1 or page + 1 == len(pagination):
                    await message.add_reaction("⬅")
                if page + 1 <= 1 or page + 1 < len(pagination):
                    await message.add_reaction("➡")
                await message.add_reaction("❌")

                await message.edit(content=None, embed=new_embed)
                await self.process_reactions(ctx, message, page, pagination, list_type)
            elif reaction.emoji == "⬅":
                page -= 1
                new_embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - {list_type} List",
                                          description="\n".join(pagination[page]),
                                          color=discord.Color.orange(),
                                          timestamp=datetime.utcnow())
                new_embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                new_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await message.clear_reactions()
                if page - 1 >= 1 or page - 1 == len(pagination):
                    await message.add_reaction("⬅")
                if page - 1 <= 1 or page + 1 < len(pagination):
                    await message.add_reaction("➡")
                await message.add_reaction("❌")

                await message.edit(content=None, embed=new_embed)
                await self.process_reactions(ctx, message, page, pagination, list_type)
            elif reaction.emoji == "❌":
                await message.delete()

    @commands.command("all", help="Gets all coronavirus information")
    async def corona_all(self, ctx):
        data = CoronaAPI().getAll()
        if data is not None:
            embed = discord.Embed(title=None, description=f"All Coronavirus (COVID-19) Information",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.add_field(name="Total Cases", value=data["cases"], inline=False)
            embed.add_field(name="Total Deaths", value=data["deaths"], inline=False)
            embed.add_field(name="Total Recoveries", value=data["recovered"], inline=False)
            await ctx.channel.send(embed=embed, content=None)
        else:
            await ctx.channel.send("Failed to get data!")

    @commands.command("country", help="Gets all coronavirus information from a country")
    async def corona_country(self, ctx, *, country):
        if country is None:
            return await ctx.channel.send("Please provide a country to get data for!")
        data = CoronaAPI().getCountry(country)
        if data is not None:
            embed = discord.Embed(title=None, description=f"All Coronavirus (COVID-19) Information in {data['country']}",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.add_field(name=f"Total Cases in {data['country']}", value=data["cases"], inline=False)
            embed.add_field(name=f"Total Cases Today in {data['country']}", value=data["todayCases"], inline=False)
            embed.add_field(name=f"Total Deaths in {data['country']}", value=data["deaths"], inline=False)
            embed.add_field(name=f"Total Deaths Today in {data['country']}", value=data["todayDeaths"], inline=False)
            embed.add_field(name=f"Total Recoveries in {data['country']}", value=data["recovered"], inline=False)
            embed.add_field(name=f"Total Critical in {data['country']}", value=data["critical"], inline=False)
            await ctx.channel.send(embed=embed, content=None)
        else:
            await ctx.channel.send("Failed to get data! Invalid country or other error occurred! use `corona "
                                   "countries` for a list of valid countries!")

    @commands.command("countries", help="Gets a list of valid countries for country command")
    async def corona_countries(self, ctx):
        data = CoronaAPI().getCountries()
        if data is not None:
            pagination = [data[i:i + 15] for i in range(0, len(data), 15)]
            page = 0

            embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - Country List",
                                  description="\n".join(pagination[page]),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            country_list_message = await ctx.send(content=None, embed=embed)
            if page + 1 <= 1 or page + 1 < len(pagination):
                await country_list_message.add_reaction("➡")
            await country_list_message.add_reaction("❌")

            await self.process_reactions(ctx, country_list_message, page, pagination, list_type="Country")
        else:
            await ctx.channel.send("Failed to get data!")

    @commands.command("states", help="Gets a list of valid states/provinces")
    async def corona_states(self, ctx):
        data = CoronaAPI().getStates()
        if data is not None:
            pagination = [data[i:i + 15] for i in range(0, len(data), 15)]
            page = 0

            embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - Province/State List",
                                  description="\n".join(pagination[page]),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            country_list_message = await ctx.send(content=None, embed=embed)
            if page + 1 <= 1 or page + 1 < len(pagination):
                await country_list_message.add_reaction("➡")
            await country_list_message.add_reaction("❌")

            await self.process_reactions(ctx, country_list_message, page, pagination, list_type="Province/State")
        else:
            await ctx.channel.send("Failed to get data!")

    @commands.command("state", help="Gets all coronavirus information from a state")
    async def corona_state(self, ctx, *, state):
        if state is None:
            return await ctx.channel.send("Please provide a state/province to get data for!")
        data = CoronaAPI().getState(state)
        if data is not None:
            embed = discord.Embed(title=None,
                                  description=f"All Coronavirus (COVID-19) Information in {data['Province/State'] + ' - ' + data['Country/Region']}",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.add_field(name=f"Total Cases in {data['Province/State'] + ' - ' + data['Country/Region']}", value=data["Confirmed"], inline=False)
            embed.add_field(name=f"Total Deaths in {data['Province/State'] + ' - ' + data['Country/Region']}", value=data["Deaths"], inline=False)
            embed.add_field(name=f"Total Recoveries in {data['Province/State'] + ' - ' + data['Country/Region']}", value=data["Recovered"], inline=False)
            await ctx.channel.send(embed=embed, content=None)
        else:
            await ctx.channel.send(
                "Failed to get data! Invalid state or other error occurred! use `corona states` for a list of valid "
                "states/provinces!")

    @commands.command("province", help="Gets all coronavirus information from a province")
    async def corona_province(self, ctx, *, province):
        if province is None:
            return await ctx.channel.send("Please provide a state/province to get data for!")
        data = CoronaAPI().getState(province)
        if data is not None:
            embed = discord.Embed(title=None,
                                  description=f"All Coronavirus (COVID-19) Information in {data['Province/State'] + '-' + data['Country/Region']}",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.add_field(name=f"Total Cases in {data['Province/State'] + '-' + data['Country/Region']}",
                            value=data["Confirmed"], inline=False)
            embed.add_field(name=f"Total Deaths in {data['Province/State'] + '-' + data['Country/Region']}",
                            value=data["Deaths"], inline=False)
            embed.add_field(name=f"Total Recoveries in {data['Province/State'] + '-' + data['Country/Region']}",
                            value=data["Recovered"], inline=False)
            await ctx.channel.send(embed=embed, content=None)
        else:
            await ctx.channel.send(
                "Failed to get data! Invalid state or other error occurred! use `corona states` for a list of valid "
                "states/provinces!")

    @commands.command("countryoverview", help="Gets all coronavirus information for each country")
    async def corona_country_overview(self, ctx):
        data = CoronaAPI().getCountriesOverview()
        if data is not None:
            pagination = [data[i:i + 15] for i in range(0, len(data), 15)]
            page = 0

            embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - Country Overview",
                                  description="\n".join(pagination[page]),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            country_list_message = await ctx.send(content=None, embed=embed)
            if page + 1 <= 1 or page + 1 < len(pagination):
                await country_list_message.add_reaction("➡")
            await country_list_message.add_reaction("❌")

            await self.process_reactions(ctx, country_list_message, page, pagination, list_type="Country Overview")
        else:
            await ctx.channel.send("Failed to get data!")


def setup(bot):
    bot.add_cog(Corona(bot))
