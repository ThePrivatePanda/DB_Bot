from nextcord.ext.commands import Cog, Bot
from ConfigHandler import Config
from DatabaseHandlers import GrinderDatabaseHandler

class GrindersConfig(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.GrindersConfig = Config("cogs/Grinders/GrindersConfig.json")
		self.bot.grinders_db: GrinderDatabaseHandler = GrinderDatabaseHandler(self.bot)

def setup(bot):
    bot.add_cog(GrindersConfig(bot))
