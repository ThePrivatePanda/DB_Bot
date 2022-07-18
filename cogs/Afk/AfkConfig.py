from nextcord.ext.commands import Cog, Bot
from nextcord import slash_command, SlashOption, Interaction, Embed, Colour, Role, Member, TextChannel
from datetime import date
from ConfigHandler import Config
from DatabaseHandlers import AFKDatabaseHandler


class AfkConfig(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.AfkConfig = Config("cogs/Afk/AfkConfig.json")
		self.bot.afk_db: AFKDatabaseHandler = AFKDatabaseHandler(self.bot)

	@slash_command(name="config_afk", guild_ids=[819084505037799465], description="Configure afk settings of the bot.")
	async def afk_config(self):...

	@afk_config.subcommand(name="get_config", description="Get the current afk config")
	async def config_counting_get_config(
		self,
		interaction: Interaction
	):
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)
		await interaction.send(self.bot.AfkConfig.config, ephemeral=True)

	@afk_config.subcommand(name="channel_ignores", description="Configure ignored channels for afk")
	async def afk_config_ignore_channel(
		self,
		interaction: Interaction,
		ignore_bool = SlashOption(
			description="Ignore the channel or unignore it (Channels ignored won't trigger afks)",
			required=True,
			choices={
				"Ignore": "True",
				"Unignore": "False"
			}
		),
		new_channel_ = SlashOption(
			description="The channel to be configured",
			required=True
		)
	):
		ignore_bool = True if ignore_bool == "True" else False

		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		try:
			new_channel: TextChannel = await self.bot.getch_channel(new_channel_)
			await new_channel.send("Ensuring I can send messages here since I'm too lazy to actually do it through permissions properly.", delete_after=0)
		except Exception as e:
			return await interaction.send(f"An error occured!\n{e}")

		l = self.bot.AfkConfig.get("ignored_channels")
		before = "Ignored" if new_channel.id in l else "Not Ignored"
		if ignore_bool:
			l.append(new_channel.id)
			self.bot.AfkConfig.update("ignored_channels", l)
		else:
			if before == "ignored":
				l.remove(new_channel.id)
				self.bot.AfkConfig.update("ignored_channels", l)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="AFK Channel Ignores Changed",
			description=f"""
Channel: {new_channel.mention}
Before: {before}
After: {"ignored" if ignore_bool else "not ignored"}

Action by: {interaction.user.mention}
""",
		colour=Colour.green())
		.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
		.set_thumbnail(url=interaction.guild.icon.url)
		)

		t = "be triggered" if ignore_bool else "not be untriggered"
		await interaction.send(f"Mentions in {new_channel.mention} will now {t}", ephemeral=True)

	@afk_config.subcommand(name="allow", description="Change who can go afk")
	async def afk_config_allow(self): ...

	@afk_config_allow.subcommand(name="role", description="Change roles that are allowed to go afk")
	async def afk_config_allow_role(
		self,
		interaction: Interaction,
		allow_bool = SlashOption(
			description="Allow or disallow the role to go afk",
			required=True,
			choices={
				"Allow": "True",
				"Disallow": "False"
			}
		),
		role_: Role = SlashOption(
			description="The role to configure the allow perms",
			required=True
		)
	):
		allow_bool = True if allow_bool == "True" else False
		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		l = self.bot.AfkConfig.get("allowed_roles")
		before = "Allowed" if role_.id in l else "Not Allowed"

		if allow_bool:
			l.append(role_.id)
			self.bot.AfkConfig.update("allowed_roles", l)
		else:
			if before == "Allowed":
				l.remove(role_.id)
				self.bot.AfkConfig.update("allowed_roles", l)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Afk Allowed Roles Changed",
			description=f"""
Role: {role_.mention}
Before: {before}
After: {"Allowed" if allow_bool else "Not Allowed"}

Action by: {interaction.user.mention}
""",
		colour=Colour.green())
		.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
		.set_thumbnail(url=interaction.guild.icon.url)
		)

		t = "able to" if allow_bool else "unable to"
		await interaction.send(f"Users with {role_.mention} will now be {t} access the afk command.", ephemeral=True)

	@afk_config_allow.subcommand(name="user", description="Change users that are allowed to go afk")
	async def afk_config_allow_users(
		self,
		interaction: Interaction,
		allow_bool = SlashOption(
			description="Allow or disallow the user to go afk",
			required=True,
			choices={
				"Allow": "True",
				"Disallow": "False"
			}
		),
		user_: Member = SlashOption(
			description="The user to configure the allow perms",
			required=True
		)
	):
		allow_bool = True if allow_bool == "True" else False

		if not (interaction.user.guild_permissions.manage_guild or interaction.user.id == self.bot.owner_id):
			return await interaction.send("Only guild managers are allowed to use this command.", ephemeral=True)

		l = self.bot.AfkConfig.get("allowed_users")
		before = "Allowed" if user_.id in l else "Not Allowed"

		if allow_bool:
			l.append(user_.id)
			self.bot.AfkConfig.update("allowed_users", l)
		else:
			if before == "Allowed":
				l.remove(user_.id)
				self.bot.AfkConfig.update("allowed_users", l)

		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
		await channel.send(embed=Embed(
			title="Afk Allowed Users Changed",
			description=f"""
User: {user_.mention}
Before: {before}
After: {"Allowed" if allow_bool else "Not Allowed"}

Action by: {interaction.user.mention}
""",
		colour=Colour.green())
		.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
		.set_thumbnail(url=interaction.guild.icon.url)
		)

		t = "able to" if allow_bool else "unable to"
		await interaction.send(f"{user_.mention} will now be {t} access the afk command", ephemeral=True)

def setup(bot):
	bot.add_cog(AfkConfig(bot))
