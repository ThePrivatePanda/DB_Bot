from nextcord.ext import commands
from nextcord import Member, Embed, Colour
import nextcord


class Welcomer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join_welcome(self, member: Member):
        channel = await self.bot.getch_channel(self.bot.config.get("welcome_channel"))

        await channel.send(
            f"Hello {member.mention}! Welcome to **{member.guild.name}**! Please verify in <#{self.bot.config.get('verify_channel')}> to get started!"
        )


    @commands.command(name="rules")
    async def rules(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")

        if here == "verify":
            channel = await self.bot.getch_channel(self.bot.config.get("verify_channel"))
        elif here == "rules":
            channel = await self.bot.getch_channel(self.bot.config.get("rules_channel"))
        else:
            channel = ctx.channel

        embed=Embed(
            title="Server Rules",
            description=f"""
<:MC_number_1:819527125576056832> Follow Discord and Bot TOS / Rules
<:MC_number_2:819527199827951616>Impersonating bots and/or members is prohibited
<:MC_number_3:819527247131181076> Use channels appropriately and within reason
<:MC_number_4:819527307605049365> Do not post NSFW or otherwise obviously unwanted material
<:MC_number_5:819527364093411329> Do not beg or cause unnecessary drama/issues
<:MC_number_6:819527410604441620> Do not use IP Grabbers, bot tokens, or release sensitive data that could damage/harm a person/thing is strictly prohibited

Please use common sense and do not create any form of unnecessary drama. The staff team holds the right to take necessary action without prior discretion.
""",        colour=0xfffa65
        ).set_footer(text="Thanks for keeping the server great!").set_thumbnail(url=self.bot.user.display_avatar.url)

        await channel.send(embed=embed)

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        if not self.bot.verify_view_set:
            self.add_view(PersistentView())
            self.bot.verify_view_set = True

    @commands.command(name="verify_menu")
    async def verify_menu(self, ctx: commands.Context):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")
        channel = await self.bot.getch_channel(self.bot.config.get("verify_channel"))
        await channel.send(content="**If you have read the rules and agree to them, click the button below.**", view=PersistentView(self.bot))

class PersistentView(nextcord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Verify", style=nextcord.ButtonStyle.green, custom_id="persistent_view:verify"
    )
    async def verify_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.user.add_roles(interaction.guild.get_role(self.bot.config.get("verified_role")))
        embed = Embed(
            title=f"Welcome to **{interaction.guild.name}**!",
            description=f"""
To get started, here is a list of popular channels below!
**➔ Main-Chat** <#{self.bot.config.get("main_chat")}>
**➔ Self-Roles** <#{self.bot.RolesConfig.get("self_roles_channel")}> or `/roles`
**➔ Perks** <#{self.bot.config.get("perks_channel")}>
**➔ Dank Board** <#{self.bot.config.get("dank_board")}>
**➔ Become Staff** <#{self.bot.config.get("apply_staff_channel")}>
**➔ Dank Committees** <#{self.bot.config.get("join_committees")}>
**➔ Events** <#{self.bot.config.get("events_channel")}>
**➔ Giveaways** <#{self.bot.config.get("giveaways_channel")}>

For any queries or problems, please visit <#{self.bot.config.get("support_channel_id")}>
Guild Invite Vanity: https://discord.gg/dankbusiness
""",
            colour=Colour.green(),
        ).set_footer(text="Dank Business | Welcome", icon_url=self.bot.user.display_avatar.url).set_thumbnail(url=interaction.guild.icon.url)

        try:
            await interaction.user.send(embed=embed)
        except:
            pass

    

def setup(bot):
    bot.add_cog(Welcomer(bot))
