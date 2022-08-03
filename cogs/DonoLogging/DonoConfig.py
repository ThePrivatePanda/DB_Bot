from nextcord.ext.commands import Cog, Bot
from ConfigHandler import Config
from DatabaseHandlers import DonoLoggingDatabaseHandler

class DonoConfig(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.DonoConfig = Config("cogs/DonoLogging/DonoConfig.json")
		self.bot.dono_db: DonoLoggingDatabaseHandler = DonoLoggingDatabaseHandler(self.bot)

def setup(bot):
    bot.add_cog(DonoConfig(bot))
