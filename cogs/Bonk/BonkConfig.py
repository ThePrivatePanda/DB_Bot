from nextcord.ext.commands import Bot, Cog
from DatabaseHandlers import RemindersDatabaseHandler

class BonkConfig(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.reminders_db: RemindersDatabaseHandler = RemindersDatabaseHandler(bot)

def setup(bot):
    bot.add_cog(BonkConfig(bot))