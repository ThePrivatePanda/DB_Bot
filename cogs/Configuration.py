from nextcord.ext.commands import Cog, Bot
from nextcord import slash_command, SlashOption, Interaction, Embed, Colour, User, ChannelType
from datetime import date
from nextcord.abc import GuildChannel

class Configuration(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

	@slash_command(name="config_counting", guild_ids=[819084505037799465], description="Configure various settings of the bot.")
	async def counting_config(self):...

	@counting_config.subcommand(name="channel", description="Change the counting channel")
	async def config_counting_channel(
		self,
		interaction: Interaction,
		new_channel_ = SlashOption(
			description="The new channel in which the bot will listen for counting messages",
			required=True
		)
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)
		try:
			old_channel = await self.bot.getch_channel(self.bot.config.get("counting_channel"))
		except:
			old_channel = None

		try:
			new_channel = await self.bot.getch_channel(new_channel_)
			await new_channel.send("Ensuring I can send messages here since I'm too lazy to actually do it through permissions properly.", delete_after=0)
		except Exception as e:
			return await interaction.send(f"An error occured!\n{e}")

		if old_channel is not None:
			await old_channel.send(embed=Embed(
				title="Counting Channel Changed",
				description=f"The counting channel has been changed from <#{old_channel}> to <#{new_channel.id}>\nCounting will now take place in the new channel.",
				colour=Colour.red()
			)
			.set_thumbnail(url=interaction.guild.icon.url)
			.set_footer(f"DB Bot | {date.today().strftime('%B %d, %Y')}"))

		await new_channel.send(embed=Embed(
			title="Counting Channel Changed",
			description=f"The counting channel has now been set to this channel. Counting will now take place in the new channel.",
			colour=Colour.green()
			).add_field(
				name="Counting Rules",
				value="""
					1) Ruining the count will get you YEET.
					2) You are allowed to count only once in a row.
					3) Don't interrupt if multiple people are already counting.""")
			.set_thumbnail(url=interaction.guild.icon.url)
			.set_footer(f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		)

		self.bot.config.update("counting_channel", new_channel.id)
		await interaction.send(f"Counting channel set to {new_channel.mention}", ephemeral=True)

	@counting_config.subcommand(name="count", description="Change the last count the bot knows of")
	async def config_counting_count(
		self,
		interaction: Interaction,
		last_count: int = SlashOption(
			description="Set the last count the bot knows of, must be an int.",
			required=True
		),
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		self.bot.config.update("counting_count", last_count)
		await interaction.send(f"Last count set to {last_count}.", ephemeral=True)

	@counting_config.subcommand(name="author", description="Change the last author of counting the bot knows of")
	async def config_counting_author(
		self,
		interaction: Interaction,
		last_count_author: User = SlashOption(
			description="Set the author of the last count the bot knows of.",
			required=True
		)
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		self.bot.config.update("counting_count_author", last_count_author.id)
		await interaction.send(f"Last author set to {last_count_author.mention}", ephemeral=True)

	@counting_config.subcommand(name="claim", description="Change the channel in which users can claim their prize")
	async def config_counting_claim(
		self,
		interaction: Interaction,
		prize_claim_channel: GuildChannel = SlashOption(
			channel_types=[ChannelType.text],
			description="Set the channel in which users are told to go to, to claim their counting prizes.",
			required=True
		)
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		try:
			old_prize_claim_channel = await self.bot.getch_channel(self.bot.config.get("prize_claim_channel_id"))
		except:
			old_prize_claim_channel = None

		if prize_claim_channel.id != old_prize_claim_channel:
			self.bot.config.update("prize_claim_channel_id", prize_claim_channel.id)
		await interaction.send(f"Counting prizes claim channel set to {prize_claim_channel.mention}", ephemeral=True)

		try:
			await prize_claim_channel.send("Ensuring I can send messages here since I'm too lazy to actually do it through permissions properly.", delete_after=0)
		except Exception as e:
			return await interaction.send(f"An error occured!\n{e}")

		if old_prize_claim_channel is not None:
			await old_prize_claim_channel.send(embed=Embed(
				title="Counting Prize Claim Channel Changed",
				description=f"To claim your counting prize, please head over to the new channel {prize_claim_channel.mention}",
				colour=Colour.red()
			).set_thumbnail(url=interaction.guild.icon.url).set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}"))

		await prize_claim_channel.send(embed=Embed(
                    title="Counting Prize CLaim Channel Changed",
                    description=f"Please claim your counting prize from here, now onwards.",
                    colour=Colour.green()
		).add_field(
                    name="How to claim",
                    value="""
				To claim your prize, simply run the following command:

				`db claim prize counting <link-to-congrats-message>`
				Make sure that the `link-to-congrats-message` is a complete link and it links to the message saying you won x prize.

				You are allowed to run the command only once every 6 hours
"""
                ).set_thumbnail(url=interaction.guild.icon.url).set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}"))
		await interaction.send(f"Claim channel has been set to {prize_claim_channel.mention}", ephemeral=True)

	@counting_config.subcommand(name="prizes", description="Configure settings related to counting prizes.")
	async def config_counting_prizes(self): ...

	@config_counting_prizes.subcommand(name="add", description="Add a prize for a certain count")
	async def config_counting_prizes_add(
		self,
		interaction: Interaction,
		count: int =  SlashOption(
			description="The count at which the new prize should be given out.",
			required=True
		),
		prize: str = SlashOption(
			description="The prize that a user wins at the given count.",
			required=True
		)
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)
		old = self.bot.config.get("counting_prizes")
		old[str(count)] = prize
		self.bot.config.update("counting_prizes", old)
		return await interaction.send("Al'dun boss", ephemeral=True)

	@config_counting_prizes.subcommand(name="remove", description="Remove a number/count from getting a prize")
	async def config_counting_prizes_remove(
		self,
		interaction: Interaction,
		count: int =  SlashOption(
			description="The count at which the new prize should be given out.",
			required=True
		),
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)
		old = self.bot.config.get("counting_prizes")
		try:
			del old[str(count)]
		except:
			pass

		self.bot.config.update("counting_prizes", old)
		return await interaction.send("Al'dun boss", ephemeral=True)








	# @config_main.subcommand(name="selfroles", description="Configure settings related to self roles or slash roles")
	# async def config_self_slash_roles(self): ...

	# @config_main.subcommand(name="grinder_config", description="Configurate grinder settings of the bot")
	# async def config(self,
	# 	interaction: Interaction,
	# 	variable = SlashOption(
	# 		description="Choose which grinders config setting to change",
	# 		required=True,
	# 		choices={
	# 			"Payments channels": "grinder_payment_channels",
	# 			"Late payments channels": "grinder_late_payment_channels",
	# 			"Grinder payments Acceptors": "grinder_payment_acceptors",
	# 			"Grinder info Log Channel": "grinder_log_channel"
	# 		}
	# 	)
	# ):
	# 	pass


def setup(bot):
	bot.add_cog(Configuration(bot))
