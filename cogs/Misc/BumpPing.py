from nextcord.ext.commands import Cog, Bot
from nextcord.ext.tasks import loop
from nextcord import Message
import time


class BumpPing(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bump_ping.start()
    


    @Cog.listener("on_message")
    async def on_message_bump_ping(self, message: Message):
        if not (
            message.author.id == 302050872383242240
            and len(message.embeds) > 0
            and "Bump done!" in message.embeds[0].description
            and message.channel.id == self.bot.config.get("bump_ping_channel")
        ):
            return
        bumper = message.interaction.user
        channel = await self.bot.getch_channel(self.bot.config.get("bump_ping_channel"))

        if not channel:
            return await self.bot.owner.send("Bump ping channel not set!")

        await channel.send(f"{bumper.mention} Thank you for bumping!\nNext bump <t:{int(time.time())+60*60*2}:R>")
        self.bot.config.update("bump_time", int(time.time()))

    @loop(seconds=5)
    async def bump_ping(self):
        if int(time.time()) - self.bot.config.get("bump_time") < 60 * 60 * 2:
            return

        channel = await self.bot.getch_channel(self.bot.config.get("bump_ping_channel"))
        if not channel:
            return await self.bot.owner.send("Bump ping channel not set!")
        if not self.bot.config.get("bump_ping_channel"):
            await channel.send("It's been two hours, anyone mind running `/bump`?")


def setup(bot: Bot):
    bot.add_cog(BumpPing(bot))
