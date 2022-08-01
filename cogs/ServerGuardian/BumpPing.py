from nextcord.ext.commands import Cog, Bot
from nextcord.ext.tasks import loop


class BumpPing(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bump_ping.start()
    
    @loop(hours=2)
    async def bump_ping(self):
        channel = await self.bot.getch_channel(self.bot.config.get("bump_ping_channel"))
        if not channel:
            return

        await channel.send("Tis been 2 hours, anyone mind running `/bump`?")

    @bump_ping.after_loop
    async def before_bump_ping(self):
        def check(m):
            m.author.id == 302050872383242240 and len(m.embeds) == 0 and m.channel.id == self.bot.config.get("bump_ping_channel")

        mes = await self.bot.wait_for("message", check=check, timeout=60*60*2)
        await mes.channel.send("Thank you for bumping! Next bump in 2 hours!")

def setup(bot: Bot):
    bot.add_cog(BumpPing(bot))