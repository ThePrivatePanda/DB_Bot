from nextcord.ext.commands import Cog, Bot
from nextcord.ext import commands
from nextcord import Embed, Colour
import nextcord

class PersistentView(nextcord.ui.View):
    def __init__(self, bot, committee):
        self.bot = bot
        self.committee = committee
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Join", style=nextcord.ButtonStyle.green, custom_id=f"persistent_view:join_committee"
    )
    async def join_committee(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.user.add_roles(interaction.guild.get_role(self.bot.config.get(f"{self.committee}_role")))
        await interaction.response.send_message("You are now a member of the committee!", ephemeral=True)

    @nextcord.ui.button(
        label="Leave", style=nextcord.ButtonStyle.red, custom_id="persistent_view:leave_committee"
    )
    async def leave_committee(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.user.remove_roles(interaction.guild.get_role(self.bot.config.get(f"{self.committee}_role")))
        await interaction.response.send_message("You are not no longer a part of the committee.", ephemeral=True)


class RandEmbds(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def on_ready_randembeds(self):
        if not self.bot.committee_view_set:
            self.add_view(PersistentView())
            self.bot.verify_view_set = True

    @commands.command(name="edc")
    async def everything_dank_committee(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")
        embed=Embed(
            title="Everything Dank Committee",
            description="Welcome to the EDC! Purely an informational committee designed for general members to stay up-to-date with everything dank and analyze/explore potential methods of success! This includes but is not limited to; update preparation, badge/prestige/market/blog analysis, and dank reddit/twitter posts!",
            colour=Colour.green()
        ).set_footer(text="Welcome to the team!").set_thumbnail(url=self.bot.user.display_avatar.url)
        channel = await self.bot.getch_channel(self.bot.config.get("committees_channel"))
        channel = channel if here else ctx.channel
        await channel.send(embed=embed, view=PersistentView(self.bot, "edc"))

    @commands.command(name="sic")
    async def server_improvement_committee(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")
        embed=Embed(
            title="Server Improvement Committee",
            description="Welcome to the SIC! Purely an informational committee designed for general members to provide feedback on all initiatives server-related including the development of our monthly budget/spending! Let us know where YOU want to see the funding (besides your wallet ofc)!",
            colour=0xfffa65
        ).set_footer(text="Welcome to the team!").set_thumbnail(url=self.bot.user.display_avatar.url)
        channel = await self.bot.getch_channel(self.bot.config.get("committees_channel"))
        channel = channel if here else ctx.channel

        await channel.send(embed=embed, view=PersistentView(self.bot, "sic"))
    
    @commands.command(name="legacy_donors")
    async def legacy_donors(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")
        embed=Embed(
            title="Legacy Donations",
            description=f"""
A legacy donor is an individual willing to donate everything they own to this server while quitting the bot.
We value such donation to the highest degree and respect the hard work you have put in and so to that, we offer you Presidential acknowledgement with your <@&{self.bot.config.get("legacy_donor_role")}> [2x Amari].
""",
            colour=0x2ecc71).set_footer(text="Thank you for choosing to support us one last time!").set_thumbnail(url=self.bot.user.display_avatar.url)
        channel = await self.bot.getch_channel(self.bot.config.get("legacy_donor_channel"))
        channel = channel if here else ctx.channel

        await channel.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(RandEmbds(bot))
