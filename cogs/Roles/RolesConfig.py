from nextcord.ext.commands import Cog, Bot
from nextcord import slash_command, Interaction, SlashOption, ChannelType, Embed, Colour
from nextcord.abc import GuildChannel
from datetime import date
from ConfigHandler import Config

class RolesConfig(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.RolesConfig = Config("cogs/Roles/RolesConfig.json")


# 	@slash_command(name="config_selfroles", guild_ids=[819084505037799465], description="Configure various settings of the bot related to slash/self roles.")
# 	async def config_selfroles(self): ...

# 	@config_selfroles.subcommand(name="channel", description="Change the channel in which selfrole messages appear. Instant changes.")
# 	async def config_selfroles_channel(
# 		self,
# 		interaction: Interaction,
# 		new_channel_: GuildChannel = SlashOption(
# 			name="New Channel",
# 			channel_types=[ChannelType.text],
# 			description="The new channel in which selfrole messages will appear",
# 			required=True
# 		)
# 	):
# 		old_channel = await self.bot.getch_channel(self.bot.SelfRolesConfig.get("selfroles_channel"))

# 		try:
# 			await new_channel_.send("Ensuring I can send messages here since I'm too lazy to actually do it through permissions properly.", delete_after=0)
# 		except Exception as e:
# 			return await interaction.send(f"An error occured!\n{e}")

# 		if old_channel is not False:
# 			for message in old_channel.history(limit=1000):
# 				if message.author.id == self.bot.user.id:
# 					await message.delete()

# 		await old_channel.send(embed=Embed(
# 			title="Selfrole channel changed",
# 			description=f"The selfrole channel has been changed from {old_channel.mention} to {new_channel_.mention}\nTo take selfroles, please go to the new channel.\nYou can also take roles by running the `/selfrole` command.",
# 			color=0x00ff00
# 			)
# 			.set_footer(text="DB Bot | Selfroles")
# 			.set_thumbnail(url=interaction.guild.icon.url)
# 		)

# 		self.bot.SelfRolesConfig.update("selfroles_channel", new_channel_.id)

# ##############################################
# #################### TODO ####################
# # Auto send the dropdowns in the new channel #
# ##############################################

# 		channel = await self.bot.getch_channel(self.bot.config.get("config_logging_channel"))
# 		await channel.send(embed=Embed(
# 			title="Counting Channel Changed",
# 			description=f"""
# Before: {old_channel.mention if old_channel is not False else "None"}
# After: {new_channel_.mention}
# Action by: {interaction.user.mention}
# """,
# 		colour=Colour.green())
# 		.set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}", icon_url=interaction.user.display_avatar.url)
# 		.set_thumbnail(url=interaction.guild.icon.url)
# 		)
# 		await interaction.send(f"Selfroles channel set to {new_channel_.mention}", ephemeral=True)






def setup(bot: Bot):
	bot.add_cog(RolesConfig(bot))