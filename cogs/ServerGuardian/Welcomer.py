from nextcord.ext import commands
from nextcord import Member

class Welcomer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join_welcome(self, member: Member):
        channel = await self.bot.getch_channel(self.bot.config.get("welcome_channel"))
        await channel.sendf(f"Hello {member.mention}! Welcome to **{member.guild.name}**! Please verify in <#{self.bot.config.get('verify_channel')}> to get started!")

        selfroles_channel = await self.bot.getch_channel(self.bot.RolesCOnfig.get("self_roles_channel"))
        await selfroles_channel.send(member.mention, delete_after=0)

def setup(bot):
    bot.add_cog(Welcomer(bot))
