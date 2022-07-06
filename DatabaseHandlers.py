from nextcord.ext.commands import Bot
import time

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

class AllowancesDatabaseHandler():
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.loop.create_task(self.startup())

	async def startup(self):
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS allowances (user_id bigint UNIQUE PRIMARY KEY, allowance bigint)")
		await self.bot.db.commit()
	
	async def get_users(self):
		cursor = await self.bot.db.execute("SELECT user_id FROM allowances")
		info = cursor.fetchall()
		return info

	async def get_allowances(self, user_id):
		cursor = await self.bot.db.execute("SELECT allowance FROM allowances WHERE user_id = ?", (user_id, ))
		info = await cursor.fetchone()
		return info

	async def add(self, user_id, amount):
		if user_id in await self.get_users():
			await self.bot.db.execute("""
				UPDATE allowances
				SET allowance = allowance + ?
				WHERE user_id = ?""",
				(
					amount,
					user_id
				)
			)
		else:
			await self.bot.db.execute("INSERT INTO allowances VALUES(?, ?)", (user_id, amount))
	
	async def remove(self, user_id, amount):
		if user_id in await self.get_users():
			await self.bot.db.execute("""
				UPDATE allowances
				SET allowance = allowance - ?
				WHERE user_id = ?""",
				(
					amount,
					user_id
				)
			)
		else:
			return False
		return True

class CountingPrizesDatabaseHandler():
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.loop.create_task(self.startup())


	async def startup(self):
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS counting_prizes_log (count bigint UNIQUE PRIMARY KEY, user_id bigint, time real)")
		await self.bot.db.commit()
	
	async def add(self, count, user_id):
		await self.bot.db.execute("INSERT INTO counting_prizes_log VALUES(?, ?, ?)", (count, user_id, time.time()))
		await self.bot.db.commit()
	
	async def get_who_changed(self, count):
		cursor = await self.bot.db.execute("SELECT user_id, time FROM counting_prizes_log WHERE count = ?", (count, ))
		info = cursor.fetchone()
		return info