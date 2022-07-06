from nextcord.ext import commands


class TwitterPing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener("on_message")
    async def on_message_twitter(self, message):
        if message.author.id == 836529215662194689 and message.channel.id == 826906143661752320:
            return await message.reply("<@&993534428666151012>")

def setup(bot: commands.Bot):
    bot.add_cog(TwitterPing(bot))
