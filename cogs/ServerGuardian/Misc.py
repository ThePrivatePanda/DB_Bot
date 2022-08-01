"""
A Basic Cog template using nextcord
"""

from nextcord.ext.commands import Cog, Bot
from nextcord.ext import commands

class Misc(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Command(name="nickname")
    async def nickname(self, ctx, *, nickname):
        assert len(nickname) <= 32
        await ctx.author.edit(nick=nickname)

def setup(bot: Bot):
    bot.add_cog(Misc(bot))
