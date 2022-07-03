from nextcord.ext.commands import Bot


class GrinderDatabaseHandler():
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.loop.create_task(self.startup())

	async def startup(self):
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS grinder_payments (user_id bigint UNIQUE PRIMARY KEY, total_paid bigint, paid_in_timeframe bigint, tier bigint)")
		await self.bot.db.commit()

	async def add(self, user_id: int, amount: int):
		await self.bot.db.execute("""
			UPDATE grinder_payments
			SET total_paid = total_paid + ?, paid_in_timeframe = paid_in_timeframe + ?
			WHERE user_id = ?""",
			(
				amount,
				amount,
				user_id
			)
		)

	async def add_late(self, user_id: int, amount: int):
		await self.bot.db.execute("""
			UPDATE grinder_payments
			SET total_paid = total_paid + ?
			WHERE user_id = ?""",
			(
				amount,
				user_id
			)
		)

	async def grinder_accept_change(self, user_id: int, tier: int):
		if user_id in await self.get_grinders():
			await self.bot.db.execute("UPDATE grinder_payments SET tier = ? WHERE user_id = ?", (tier, user_id))
		else:
			await self.bot.db.execute("INSERT INTO grinder_payments VALUES(?, ?, ?, ?)", (user_id, 0, 0, tier))
		await self.bot.db.commit()

	async def get_info(self, user_id: int):
		cursor = await self.bot.db.execute("SELECT total_paid, paid_in_timeframe, tier FROM grinder_payments WHERE user_id = ?", (user_id, ))
		info = await cursor.fetchone()
		return info

	async def get_grinders(self):
		cursor = await self.bot.db.execute("SELECT user_id FROM grinder_payments")
		info = cursor.fetchall()
		return info
