"""Configurations Used:
Config -
	config_logging_channel      int    - The channel in which the bot logs changes
"""

from re import T
from nextcord.ext.commands import Cog, Bot
from nextcord import slash_command, SlashOption, Interaction, Embed, Colour, User, ChannelType, Role, File
from datetime import date
from nextcord.abc import GuildChannel
from ConfigHandler import Config
import io
from DatabaseHandlers import CountingPrizesDatabaseHandler

class CountingConfig(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.CountingConfig: Config = Config("cogs/Counting/CountingConfig.json")
		self.bot.counting_db: CountingPrizesDatabaseHandler = CountingPrizesDatabaseHandler(bot)


	@slash_command(name="prize_history", guild_ids=[819084505037799465], description="Get who changed/set the prize for a count")
	async def prize_history(
		self, 
		interaction: Interaction, 
		count: int = SlashOption(
			description="Check who last changed/set a counting prize.",
			required=False)
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		if count:
			r = await self.bot.counting_db.get(count)
			if r:
				user_id, time = r
			else:
				await interaction.send("I don't have any info on that count.", ephemeral=True)
			await interaction.send(f"The prize was set by <@{user_id}> at time: <t:{int(time)}:f> (Localized time)", ephemeral=False)
		else:
			_all = await self.bot.counting_db.get_all()
			info = []
			for count, user_id, time in _all:
				info.append(f"{count}: <@{user_id}> at time: <t:{int(time)}:f>")
			info = "\n".join(info)
			if len(info) > 2000:
				info = []
				for count, user_id, time in _all:
					user = await self.bot.getch_user(user_id)
					time = date.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")
					info.append(f"{count}: {user.name}#{user.discriminator} ({user.id}) at time: {time}")
				info = "\n".join(info)
				buf = io.BytesIO(bytes(info, "utf-8"))
				await interaction.send(file=File(buf, "prize_change_history.txt"), ephemeral=False)
			else:
				await interaction.send(f"{info}", ephemeral=True)

	@slash_command(name="config_counting", guild_ids=[819084505037799465], description="Configure counting settings of the bot.")
	async def counting_config(self):...

	@counting_config.subcommand(name="get_config", description="Get the current counting config")
	async def config_counting_get_config(
		self,
		interaction: Interaction,
		variable: str = SlashOption(
			description="Get the value of a config variable",
			required=False,
			choices={
				"Channel": "counting_channel",
				"Words Allowed Role": "words_allowed_role",
				"Count": "counting_count",
				"Count Author": "counting_count_author",
				"Prizes": "counting_prizes",
				"Prize claim channel": "prize_claim_channel_id",
				"Event Blacklist Role": "events_blacklist_role",
				"Support Channel": "support_channel",
			}
		)
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)
		if variable:
			await interaction.send(self.bot.CountingConfig.get(variable), ephemeral=True)
		else:
			await interaction.send(self.bot.CountingConfig.config, ephemeral=True)

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
			old_channel = await self.bot.getch_channel(self.bot.CountingConfig.get("counting_channel"))
		except:
			old_channel = None

		try:
			new_channel = await self.bot.getch_channel(new_channel_)
			await new_channel.send("Ensuring I can send messages here since I'm too lazy to actually do it through permissions properly.", delete_after=0)
		except Exception as e:
			return await interaction.send(f"An error occured!\n{e}")

		if old_channel is True:
			await old_channel.send(embed=Embed(
				title="Counting Channel Changed",
				description=f"The counting channel has been changed from <#{old_channel}> to <#{new_channel.id}>\nCounting will now take place in the new channel.",
				colour=Colour.red()
			)
			.set_thumbnail(url=interaction.guild.icon.url)
			.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}"))

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
			.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		)

		self.bot.CountingConfig.update("counting_channel", new_channel.id)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Counting Channel Changed",
			description=f"""
Before: <#{old_channel}>
After: <#{new_channel}>
Action by: {interaction.user.mention}
""",
		colour=Colour.green())
		.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
		.set_thumbnail(url=interaction.guild.icon.url)
		)
		await interaction.send(f"Counting channel set to {new_channel.mention}", ephemeral=True)

	@counting_config.subcommand(name="words_allowed", description="Change the last count the bot knows of")
	async def config_counting_words_allowed(
		self,
		interaction: Interaction,
		role: Role = SlashOption(
			description="Users with this role can send words in the counting channel.",
			required=True
		),
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		old_role = self.bot.CountingConfig.get("words_allowed_role")
		self.bot.CountingConfig.update("words_allowed_role", role.id)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Counting Words Allow Role Changed",
			description=f"""
Before: <@&{old_role}>
After: {role.men}
Action by: {interaction.user.mention}
""",
		colour=Colour.green())
		.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
		.set_thumbnail(url=interaction.guild.icon.url)
		)

		await interaction.send(f"Users with `{role.name}` will now be able to send words in the counting channel.", ephemeral=True)

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

		old_count = self.bot.CountingConfig.get("counting_count")
		self.bot.CountingConfig.update("counting_count", last_count)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Counting Count Changed",
			description=f"""
Before: `{old_count}`
After: `{last_count}`
Action by: {interaction.user.mention}
""",
			colour=Colour.green())
			.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
			.set_thumbnail(url=interaction.guild.icon.url)
		)

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

		old_author = self.bot.CountingConfig.get("counting_count_author")
		self.bot.CountingConfig.update("counting_count_author", last_count_author.id)
		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Last Count Author Changed",
			description=f"""
Before: <@{old_author}>
After: {last_count_author.mention}
Action by: {interaction.user.mention}
""",
			colour=Colour.green())
			.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
			.set_thumbnail(url=interaction.guild.icon.url)
		)

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
			old_prize_claim_channel = await self.bot.getch_channel(self.bot.CountingConfig.get("prize_claim_channel_id"))
		except:
			old_prize_claim_channel = None

		if prize_claim_channel.id == old_prize_claim_channel.id:
			return await interaction.send("The channel you specified is already the channel in which users can claim their prizes.", ephemeral=True)

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

		self.bot.CountingConfig.update("prize_claim_channel_id", prize_claim_channel.id)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Counting Prize Claim Channel Changed",
			description=f"""
Before: {old_prize_claim_channel.mention if old_prize_claim_channel is not None else "None"}
After: {prize_claim_channel.mention}
Action by: {interaction.user.mention}
""",
			colour=Colour.green())
			.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
			.set_thumbnail(url=interaction.guild.icon.url)
		)
		await interaction.send(f"Counting prizes claim channel set to {prize_claim_channel.mention}", ephemeral=True)

	@counting_config.subcommand(name="prizes", description="Add/Rem a prize for a certain count")
	async def config_counting_prizes(
		self,
		interaction: Interaction,
		add_or_remove = SlashOption(
			description="Add or remove a prize for a certain count",
			required=True,
			choices={
				"add_or_change": "add",
				"remove": "remove"
			}
		),
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

		old = self.bot.CountingConfig.get("counting_prizes")
		if str(count) in old.keys():
			old_prize = old[str(count)]
		else:
			old_prize = None

		if add_or_remove == "add":
			old[str(count)] = prize
		else:
			if str(count) in old.keys():
				del old[str(count)]
		self.bot.CountingConfig.update("counting_prizes", old)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Counting Prize Changed",
			description=f"""
Count: `{count}`
Before: {old_prize if old_prize is not None else "None"}
After: {prize if add_or_remove == "add" else "None"}
Action by: {interaction.user.mention}
""",
			colour=Colour.green())
			.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
			.set_thumbnail(url=interaction.guild.icon.url)
		)

		return await interaction.send(f"Al'dun boss\n{old}", ephemeral=True)

def setup(bot):
	bot.add_cog(CountingConfig(bot))
