"""Configurations Used:
grinder_payment_channels        list[int] - The channels in which the bot listens for grinder payments
grinder_late_payment_channels   list[int] - The channels in which the bot listens for late grinder payments
grinder_payment_acceptors       list[int] - Authorized users which take grinder payments. Payments to other users will not be loggged towards grinder payments.
grinder_log_channel             int       - The channel in which logs of grinder payments are sent
grinder_payment_requirements    dict[tier: str, amount: int] - The amount of payment required by grinders per tier
"""
"""Needa do:
- lb system
- get stats on command
- accept/deny grinders
- auto perk claims?
- white list grinders who paid, for taking perks.
"""
from nextcord.ext.commands import Cog, Bot
from nextcord import Message, Embed, User, Colour
from datetime import date
import datetime

from nextcord.ext import tasks

class Grinders(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

	async def accept_grinder(self, user_id: int, tier: int):
		await self.bot.grinders_db.grinder_accept_change(user_id, tier)

	
	async def process_payment(self, message: Message, payee, acceptor, cash):

		await self.bot.grinders_db.add(payee.id, cash)
		total_paid, week_payment, tier = await self.bot.grinders_db.get_info(payee.id)

		log_channel = await self.bot.getch_channel(self.bot.config.get("grinder_log_channel"))
		required = self.bot.config.get("grinder_payment_requirements")[str(tier)]
		requirement_left = required - week_payment

		if requirement_left > 0:
			left = f"Payment left: ⏣ {requirement_left:3,}"
		else:
			left = "Payment left: None!"

		await log_channel.send(
			embed=Embed(
				title="Grinder Payment Received",
				description=f"""
User: {payee.mention}
Paid Now: **⏣ {cash:3,}**
Total Paid: **⏣ {total_paid:3,}**
Week Payment: **⏣ {week_payment:3,}**
Current Tier: `{tier}`

[Trade Link]({message.jump_url})
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
You have paid a total of **⏣ {(total_paid):3,}**.
You have paid **⏣ {(week_payment):3,}** this week.

Your current grinder tier is: `{tier}`
""",

				colour=0x00FF00
			)
			.set_thumbnail(message.guild.icon.url)
			.set_footer(icon_url=payee.display_avatar.url, text=left)
		)
		return

	async def process_late_payment(self, message: Message, payee, acceptor, cash):
		
		await self.bot.grinders_db.add_late(payee.id, cash)
		total_paid, tier = await self.bot.grinders_db.get_info(payee.id)

		log_channel = await self.bot.getch_channel(self.bot.config.get("grinder_log_channel"))
		required = self.bot.config.get("grinder_payment_requirements")[str(tier)]

		left = f"Payment left: ⏣ {required:3,}"


		await log_channel.send(
			embed=Embed(
				title="Late Grinder Payment Received",
				description=f"""
User: {payee.mention}
Paid now: **⏣ {cash:3,}**
Total Paid: **⏣ {total_paid:3,}**
Current Tier: `{tier}`

[Trade Link]({message.jump_url})
Accepted By: {acceptor.mention}
""",
                            colour=Colour.red()
			)
			.set_thumbnail(payee.display_avatar.url)
			.set_footer(icon_url=message.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}"))

		await message.channel.send(
			content=payee.mention,
			embed=Embed(
				title="Grinder Payment logged successfully!",
				description=f"""
Your payment of **⏣ {cash:3,}** for last week has been logged successfully.
You have paid a total of **⏣ {(total_paid):3,}**.

Please keep your payments on time, repeated late payments may result in moderation actions against you.
Your current grinder tier is: `{tier}`
""",
				colour=0xfffa65
			)
			.set_thumbnail(message.guild.icon.url)
			.set_footer(icon_url=payee.display_avatar.url, text=left)
		)
		return


	@Cog.listener("on_message_edit")
	async def on_message_edit_grinder_payment(self, before: Message, message: Message):
		if message.author.id != 270904126974590976:
			return
		if len(message.embeds) != 1 or len(message.raw_mentions) != 1:
			return
		if not (
				message.channel.id in self.bot.config.get("grinder_payment_channels")
				or message.channel.id in self.bot.config.get("grinder_late_payment_channels")
			):
			return
		if message.raw_mentions[0] not in self.bot.config.get("grinder_payment_acceptors"):
			return
		if not  message.reference:
			return
		if "Action Confirmed" not in message.embeds[0].title or "Continue trade?" not in message.embeds[0].description:
			return

		embed = message.embeds[0]
		payee: User = await self.bot.getch_member(message.guild.id, message.reference.resolved.author.id)
		acceptor = message.guild.get_member(message.raw_mentions[0])

		cash = [str(i) for i in embed.description.split(
			"⏣")[1].split("\n")[0].replace(",", "").replace(" ", "") if i.isdigit()]
		cash = int(''.join(cash))

		if "x" in embed.description.split("gives:")[1].split("<@")[0].replace("x", ""):
			return await message.channel.send(f"{payee.mention} Auto grinder payment logging in items calculation is not yet supported.\n{acceptor.mention} Please run `db grinders add {payee.mention} amount` to manually add the amount.")

		if message.channel.id in self.bot.config.get("grinder_payment_channels"):
			await self.process_payment(message, payee, acceptor, cash)
		else:
			await self.process_late_payment(message, payee, acceptor, cash)

	@tasks.loop(time=datetime.time(0, 0, 0, 0, datetime.timezone.utc))
	async def reset_grinder_weekly(self):
		pass


def setup(bot):
  bot.add_cog(Grinders(bot))