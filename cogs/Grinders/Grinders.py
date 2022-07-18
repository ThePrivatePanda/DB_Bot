from asyncio import tasks
from sys import excepthook
from typing import Literal, Optional
from discord import Colour
from nextcord.ext.commands import Cog, Bot
from nextcord.ext import commands
from nextcord import Embed, Interaction, User
import nextcord


class BecomeAGrinder(nextcord.ui.View):
	def __init__(self, bot: Bot):
		super().__init__(timeout=None)
		self.bot = bot


	async def becomagrinder(self, interaction: Interaction, tier: str):
		current_grinders = await self.bot.grinders_db.get_grinders()
		if interaction.user.id in current_grinders:
			grinder_info = await self.bot.grinders_db.get_info(interaction.user.id)
			if str(grinder_info[4]) == tier:
				return interaction.send("You are already a grinder at that tier!", ephmeral=False)
			else:
				perks_allowed = "False" if grinder_info[0] == "False" else "True"
				await self.bot.grinders_db.accept_change(interaction.user.id, tier, perks_allowed)
				if perks_allowed == "True":
					await interaction.user.add_roles(self.bot.GrindersConfig.get("tier_role_mapping")[tier])
		else:
			await self.bot.grinders_db.accept_change(interaction.user.id, tier, "False")

		await interaction.user.edit(roles=[
			j for j in interaction.user.roles if j.id not in
			self.bot.GrindersConfig.get("tier_role_mapping").values()])

		await interaction.user.add_roles(self.bot.guild.get_role(self.bot.GrindersConfig.get("pending_grinder")))

	@nextcord.ui.button(label="T1", style=nextcord.ButtonStyle.green, custom_id="grinder_t1")
	async def t1(self, button: nextcord.ui.Button, interaction: Interaction):
		await self.becomagrinder(interaction, "1")
		await interaction.send(f"Congrats! You are now a **Tier 1 grinder**! You can access all the perks after a successful payment!\nHead over to {' or, '.join([f'<#{id}>' for id in self.bot.GrindersConfig.get('grinder_payment_channels')])} for information on payments!", ephemeral=True)

	@nextcord.ui.button(label="T2", style=nextcord.ButtonStyle.green, custom_id="grinder_t2")
	async def t2(self, button: nextcord.ui.Button, interaction: Interaction):
		await self.becomagrinder(interaction, "2")
		await interaction.send(f"Congrats! You are now a **Tier 2 grinder**! You can access all the perks after a successful payment!\nHead over to {' or, '.join([f'<#{id}>' for id in self.bot.GrindersConfig.get('grinder_payment_channels')])} for information on payments!", ephemeral=True)

	@nextcord.ui.button(label="Resign", style=nextcord.ButtonStyle.red, custom_id="grinder_resign")
	async def resign(self, button: nextcord.ui.Button, interaction: Interaction):
		await self.bot.grinders_db.forget_grinder(interaction.user.id)
		l = list(self.bot.GrindersConfig.get("tier_role_mapping").values())
		l.append(self.bot.GrindersConfig.get("pending_grinder"))
		await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in l])
		await interaction.send("You are now no longer a grinder. Simply select the tier again to restore your progress and your perks.", ephemeral=True)


class Grinders(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.GrinderViewsAdded = False
		self.bot.loop.create_task(self.create_views())

	async def create_views(self):
		await self.bot.wait_until_ready()
		if not self.GrinderViewsAdded:
			self.bot.add_view(BecomeAGrinder(self.bot))
	
	def beautify_top_10(self, data):
		h = []
		for i in data:
			h.append(f"<@{i[0]}>: ⏣{i[1]}")
		return "\n".join(h)

	async def yeet(self, user_id: int):
		user: Optional[User] = await self.bot.getch_user(user_id)
		if user is None:
			return

		await user.edit(roles=[
			j for j in user.roles if j.id not in
			self.bot.GrindersConfig.get("tier_role_mapping").values()])
		try:
			await user.send(embed=Embed(
				title="Incomplete Grinder Payment",
				description=f"""
We hate to say this but you have not completed your payment, which has led to your perks being revoked.
If you wish to continue supporting us (which we hope you do), please head over to <#{self.bot.GrindersConfig.get('info_channel')}> to start over!
Please note that your lifetime payments have been saved!
""",
				colour=0xe74c3c).set_footer(text="DB Bot | Grinders", icon_url=self.bot.owner.display_avatar.url).set_thumbnail(url=self.bot.guild.icon.url)
				)
		except:
			pass

	@tasks.loop(weeks=1)
	async def wipe_grinder_db(self):
		for user_id, paid, tier in await self.bot.grinders_db.get_all_payments():
			requirement = self.bot.GrindersConfig.get("payment_requirements")[str(tier)]
			if paid < requirement:
				await self.yeet(user_id)

		top_10_weekly = await self.bot.grinders_db.get_top_10_weekly()
		top_10_lifetime = await self.bot.grinders_db.get_top_10_lifetime()
		await self.bot.grinders_db.wipe_grinder_db()
		channels = [await self.bot.getch_channel(id) for id in self.bot.GrindersConfig.get("payment_channels")]
		for channel in channels:
			if channel is not None:
				m = await channel.send(embed=Embed(
					title="Grinder Leaderboard",
					colour=0xfffa65)
					.add_field(name="Lifetime Leaderboard", value=self.beautify_top_10(top_10_lifetime)
					.add_field(name="Weekly Leaderboard", value=self.beautify_top_10(top_10_weekly))
					.set_footer(text="DB Bot | Wipeed Grinder DB", icon_url=self.bot.owner.display_avatar.url)
					.set_thumbnail(url=self.bot.guild.icon.url)
					)
				)
				try:
					await m.pin()
				except:
					pass

	@commands.command(name="grinder_pay")
	async def grinder_pay(self, ctx: commands.Context, arg: Literal["channels, users"]):
		if arg == "channels":
			return await ctx.send(f"Payment channels: {', '.join([f'<#{id}>' for id in self.bot.GrindersConfig.get('payment_channels')])}")
		elif arg == "users":
			return await ctx.send(f"Payment acceptors: {', '.join([f'<@{id}>' for id in self.bot.GrindersConfig.get('payment_acceptors')])}")
		return await ctx.send("Invalid argument")

	@commands.command(name="payment_info")
	async def payment_info_embed(self, ctx: commands.Context):
		if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
			return await ctx.reply("Only guild managers are allowed to use this command.", ephemeral=True)

		embed = Embed(
			title="Payment Info",
			description="""
If you can see this, thanks for supporting us!

For smooth operation of the bot, we ask you to adhere to some guidelines while doing your payments.
Most importantly, payments are logged only if they occur in the correct channel and to the right person.

To check channels in which payments are accepted, use the command `db grinder_pay channels`.
To check users authorized to accept payements, use the command `db grinder_pay users`.

We **recommend** to keep your DMs open to avoid any issues, as you may not recieve crucial information if the bot is unable to send messages to you.
""",
			colour=0xfffa65
		).set_footer(text="DB Bot | Payment Info", icon_url=self.bot.owner.display_avatar.url).set_thumbnail(url=self.bot.guild.icon.url)

		for channel_id in self.bot.GrindersConfig.get("payment_channels"):
			channel = await self.bot.getch_channel(channel_id)
			if channel is not None:
				await channel.send(embed=embed)

	@commands.command(name="grinder_menu")
	@commands.is_owner()
	async def grinder_menu(self, ctx):
		channel = await self.bot.getch_channel(self.bot.GrindersConfig.get("info_channel"))

		e1 = Embed(
			title="Company Support Team!", 
			description="Hey! **Got extra cash?** We need supporters like you to keep this server running as smoothly as possible! We've included a **list of benefits for each tier** so members can decide which one it is they prefer to do, but any help at all is much appreciated! **Check it out!**",
			colour=0xfffa65
		).set_thumbnail(ctx.guild.icon.url).set_footer(text="Thank you for keeping the server great!")

		t1 = Embed(
			title="T1 Benefits",
			description=f"""
**Weekly Payment: {int(self.bot.GrindersConfig.get("payment_requirements")["1"]):3,}**
<:MC_arrowbrown:842539492228202496> <@&{self.bot.GrindersConfig.get('tier_role_mapping')["1"]}> role
<:MC_arrowbrown:842539492228202496> Granted Premium Colors
<:MC_arrowbrown:842539492228202496> **Exclusive giveaways!**
<:MC_arrowbrown:842539492228202496> Amari **x3** Dank Channel
""",
			colour=0x92761f).set_thumbnail("https://images-ext-1.discordapp.net/external/ynJKJOrsOa4zHbLknUsJqqtgr_ZWs4J9Tl9M2GmFEe8/https/i.imgur.com/X7VC4Nl.jpg")
		t2 = Embed(
			title="T2 Benefits",
			description=f"""
**Weekly Payment: {int(self.bot.GrindersConfig.get("payment_requirements")["2"]):3,}**
<:MC_arrowgrey:842539204726489149> <@&{self.bot.GrindersConfig.get('tier_role_mapping')["2"]}> role
<:MC_arrowgrey:842539204726489149> Access to AFK command
<:MC_arrowgrey:842539204726489149> **Exclusive Dank strategy/tips**
<:MC_arrowgrey:842539204726489149> Granted unique auto-reaction
<:MC_arrowgrey:842539204726489149> **Bypass all server giveaway requirements**
""",
			colour=0xcccac9).set_thumbnail("https://images-ext-1.discordapp.net/external/bP3zj0IqO7NBdp05XvYOww3CfJFQaY6BBfg76gRJ780/https/i.imgur.com/yKkWAHx.jpg")

		wannabe = Embed(
			title="Want to be a grinder?",
			description="Click the respective button for which tier you would like to apply to be a grinder.\nYou will be able to access perks after your first complete payment!",
			colour=0x75ff96).set_thumbnail(ctx.guild.icon.url).set_footer(text="DB Bot | Grinders")

		await channel.send(embeds=[e1, t1, t2])
		await channel.send(embed=wannabe, view=BecomeAGrinder(self.bot))


def setup(bot: Bot):
	bot.add_cog(Grinders(bot))