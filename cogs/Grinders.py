from nextcord.ext.commands import Cog, Bot
from nextcord import Message, Embed
from datetime import date


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
			total_paid, week_payment, tier = await self.bot.grinders_db.get_info(payee.id)
			required = self.bot.config.get("grinder_payment_requirements")[str(tier)]
			requirement_left = required - week_payment + cash
			if requirement_left > 0:
				left = f"Payment left: ⏣ {requirement_left:3,}"
			else:
				left = "You've reached the weekly grinder payment requirement! Nice!"

			await log_channel.send(
				embed=Embed(
					title="Grinder Payment Received",
					description=f"""
User: {payee.mention}
Total Paid: **⏣ {total_paid+cash}**
Week Payment: **⏣ {week_payment+cash}**
Current Tier: `{tier}`

Accepted By: {acceptor.mention}
""",
				colour=0xfffa65
				)
				.set_thumbnail(payee.display_avatar.url)
				.set_footer(icon_url=message.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}"))
			await message.channel.send(
				content=payee.mention,
				embed=Embed(
					title="Grinder Payment logged successfully!",
					description=f"""
Your payment of **⏣ {cash:3,}** has been logged successfully.
You have paid a total of **⏣ {(total_paid+cash):3,}**.
You have paid **⏣ {(week_payment+cash):3,}** this week.

Your current grinder tier is: `{tier}`
""",

					colour = 0x00FF00
				)
				.set_thumbnail(message.guild.icon.url)
				.set_footer(icon_url=payee.display_avatar.url, text=left)
			)
			return

def setup(bot):
  bot.add_cog(Grinders(bot))