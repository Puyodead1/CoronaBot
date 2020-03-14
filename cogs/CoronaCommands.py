#  Copyright (C) 2020  Puyodead1
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio

import discord
from discord.ext import commands
from datetime import datetime

import Utils
from Utils import getLogger, CoronaAPI
from discord.errors import HTTPException, Forbidden, InvalidArgument


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
            try:
                await ctx.send(content=None, embed=embed)
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")
        else:
            try:
                await ctx.send("Failed to get data!")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")

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
            try:
                await ctx.send(content=None, embed=embed)
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")
        else:
            try:
                await ctx.send("Failed to get data! Invalid country or other error occurred! use `corona "
                                   "countries` for a list of valid countries!")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")

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

            try:
                country_list_message = await ctx.send(content=None, embed=embed)
                if page + 1 <= 1 or page + 1 < len(pagination):
                    await country_list_message.add_reaction("➡")
                await country_list_message.add_reaction("❌")

                await self.process_reactions(ctx, country_list_message, page, pagination, list_type="Country")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")
        else:
            try:
                await ctx.send("Failed to get data")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")

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

            try:
                country_list_message = await ctx.send(content=None, embed=embed)
                if page + 1 <= 1 or page + 1 < len(pagination):
                    await country_list_message.add_reaction("➡")
                await country_list_message.add_reaction("❌")

                await self.process_reactions(ctx, country_list_message, page, pagination, list_type="Province/State")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")
        else:
            try:
                await ctx.send("Failed to get data!")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")

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
            try:
                await ctx.send(content=None, embed=embed)
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")
        else:
            try:
                await ctx.send(
                "Failed to get data! Invalid state or other error occurred! use `corona states` for a list of valid "
                "states/provinces!")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")

    @commands.command("province", help="Gets all coronavirus information from a province")
    async def corona_province(self, ctx, *, province):
        if province is None:
            return await ctx.send("Please provide a state/province to get data for!")
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
            try:
                await ctx.send(content=None, embed=embed)
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")
        else:
            try:
                await ctx.send(
                "Failed to get data! Invalid state or other error occurred! use `corona states` for a list of valid "
                "states/provinces!")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")

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

            try:
                country_list_message = await ctx.send(content=None, embed=embed)
                if page + 1 <= 1 or page + 1 < len(pagination):
                    await country_list_message.add_reaction("➡")
                await country_list_message.add_reaction("❌")

                await self.process_reactions(ctx, country_list_message, page, pagination, list_type="Country Overview")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")
        else:
            try:
                await ctx.send("Failed to get data!")
            except Forbidden as e:
                await ctx.send(content=f"Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(content=f"Failed to send message! Error: {e.text}")


def setup(bot):
    bot.add_cog(Corona(bot))
