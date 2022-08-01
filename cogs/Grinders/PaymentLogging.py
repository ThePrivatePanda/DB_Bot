from nextcord.ext.commands import Cog, Bot
from nextcord import Message, Embed, User, Colour
from datetime import date
import pendulum


class GrindersPaymentLogging(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.process_payment = self.process_payment

	async def process_payment(self, message: Message, payee: User, acceptor: User, cash: int):
		await self.bot.grinders_db.add(payee.id, cash)
		h = await self.bot.grinders_db.get_info(payee.id)
		total_paid, week_payment, tier = h[2], h[3], h[4]

		log_channel = await self.bot.getch_channel(self.bot.GrindersConfig.get("log_channel"))
		required = self.bot.GrindersConfig.get("payment_requirements")[str(tier)]
		requirement_left = required - week_payment

		if requirement_left > 0:
			left = f"Payment left: ⏣ {requirement_left:3,}"
		else:
			left = "Completed payment requirement!"

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

		await self.bot.grinders_db.add(payee.id, cash)
		next_saturday = pendulum.now(tz="GMT").next(pendulum.SATURDAY).timestamp()-1

		if requirement_left > 0:
			m = f"Your payment of **⏣{cash:3,}** has been received and logged successfully.\n You have until <t:{int(next_saturday)}:F> to complete your payment of **⏣{requirement_left:3,}**"
		else:
			m = "Your payment has been received and logged successfully.\n You have **completed your payment** requirement for this week!\n**Your perks have been auto claimed**, Enjoy!"
			await self.bot.grinders_db.accept_change(payee.id, tier, "True")
			roles = payee.roles
			roles.append(self.bot.getch_role(self.bot.GrindersConfig.get("tier_role_mapping")(str(tier))))
			await payee.add_roles(roles)

		try:
			await payee.send(embed=Embed(
				title="Grinder Payment Received",
				description=(m+f"\nYour **weekly** ranking is: `{await self.bot.grinders_db.get_ranking_weekly(payee.id)}` and your **monthly** ranking is `{await self.bot.grinders_db.get_ranking_monthly(payee.id)}`"),
				colour=0x2ecc71
				).set_footer(text="Thanks for supporting us!", icon_url=payee.display_avatar.url).set_thumbnail(url=self.bot.guild.icon.url)
			)
		except:
			pass


		return

	@Cog.listener("on_message_edit")
	async def on_message_edit_grinder_payment(self, before: Message, message: Message):
		if message.author.id != 270904126974590976:
			return
		if len(message.embeds) != 1 or len(message.raw_mentions) != 1:
			return
		if message.channel.id not in self.bot.GrindersConfig.get("payment_channels"):
			return
		if message.raw_mentions[0] not in self.bot.GrindersConfig.get("payment_acceptors"):
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

		await self.process_payment(message, payee, acceptor, cash)

def setup(bot):
  bot.add_cog(GrindersPaymentLogging(bot))