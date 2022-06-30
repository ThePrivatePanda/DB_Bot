from nextcord.ext.commands import Cog, Bot
from nextcord import Message, Embed

class Grinders(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_message_edit")
    async def on_message_edit_grinder_payment(self, before: Message, message: Message):
        if (
            message.author.id != 270904126974590976
            or len(message.embeds) != 1 or len(message.mentions) != 1
            or not (
                message.channel.id in self.bot.config.get("grinder_payment_channels")
                or message.channel.id in self.bot.config.get("grinder_late_payment_channels")
            )
            or message.mentions[0].id not in self.bot.config.get("grinder_payment_acceptors")
            or not message.reference
            or "Action Confirmed" not in message.embeds[0].title
            or "Continue trade?" not in message.embeds[0].description
        ):
            embed = message.embeds[0]
            payee = await self.bot.getch_member(message.guild.id, message.reference.resolved.author.id)
            acceptor = message.mentions[0]
            cash = int(embed.description.split("⏣")[1].split("\n")[0].replace(",", "").replace(" ", ""))
            if "x" in embed.description:
                return await message.channel.send(f"{payee.mention} Auto grinder payment logging in items calculation is not yet supported.\n{acceptor.mention} Please run `db grinders add {payee.mention} amount` to manually add the amount.")
            await self.bot.grinders_db.add(payee.id, cash)
            log_channel = await self.bot.getch_channel(self.bot.config.get("grinder_log_channel"))
            await log_channel.send(
                embed=Embed(
                    title="Grinder Payment Received",
                    description="").set_thumbnail(p))
            return

def setup(bot):
  bot.add_cog(Grinders(bot))