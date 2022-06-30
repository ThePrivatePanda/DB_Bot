from nextcord.ext.commands import Cog, Bot
from nextcord.ext import commands
from nextcord import slash_command, SlashOption, Interaction


class Configurationg(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

	@slash_command(name="config", guild_ids=[819084505037799465], description="Configure various settings of the bot.")
	async def config_main(self, interaction: Interaction):
		pass
	@config_main.command(name="grinder_config", description="Configurate grinder settings of the bot")
	async def config(self,
		interaction: Interaction,
		variable = SlashOption(
			description="Choose which grinders config setting to change",
			required=True,
			choices={
				"Payments channels": "grinder_payment_channels",
				"Late payments channels": "grinder_late_payment_channels",
				"Grinder payments Acceptors": "grinder_payment_acceptors",
				"Grinder info Log Channel": "grinder_log_channel"
			}
		)
	):
		pass


def setup(bot):
	bot.add_cog(Configurationg(bot))