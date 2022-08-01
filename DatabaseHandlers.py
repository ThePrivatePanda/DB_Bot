from lib2to3.pgen2.token import AWAIT
from sys import int_info
from nextcord.ext.commands import Bot
import time
from typing import Any, Literal


class GrinderDatabaseHandler():
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		self.bot.loop.create_task(self.startup())

	async def startup(self) -> None:
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS grinder_payments (user_id bigint UNIQUE PRIMARY KEY, perks_allowed text, start_time bigint, total_paid bigint, paid_in_timeframe bigint, tier bigint)")
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS resigned_grinders (user_id bigint UNIQUE PRIMARY KEY, perks_allowed text, end_time bigint, total_paid bigint, paid_in_timeframe bigint, tier bigint)")
		await self.bot.db.commit()
	
	async def wipe_weekly(self):
		await self.bot.db.execute("DROP TABLE IF EXISTS grinder_payments")
		await self.bot.db.commit()
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS grinder_payments (user_id bigint UNIQUE PRIMARY KEY, perks_allowed text, start_time bigint, total_paid bigint, paid_in_timeframe bigint, tier bigint)")
		await self.bot.db.commit()


	async def add(self, user_id: int, amount: int) -> None:
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

	async def add_late(self, user_id: int, amount: int) -> None:
		await self.bot.db.execute("""
			UPDATE grinder_payments
			SET total_paid = total_paid + ?
			WHERE user_id = ?""",
								  (
									  amount,
									  user_id
								  )
								  )

	async def forget_grinder(self, user_id: int) -> None:
		info = await self.get_info(user_id)
		if not info:
			return
		perks_allowed, tier = info[0], info[4]
		total_paid, paid_in_timeframe = info[2], info[3]
		await self.bot.db.execute("DELETE FROM grinder_payments WHERE user_id = ?", (user_id, ))
		await self.bot.db.execute("INSERT INTO resigned_grinders VALUES(?, ?, ?, ?, ?, ?)", (user_id, perks_allowed, time.time(), total_paid, paid_in_timeframe, tier))

	async def accept_change(self, user_id: int, tier: int, perks_allowed: str) -> None:
		await self.bot.db.execute("DELETE FROM resigned_grinders WHERE user_id = ?", (user_id, ))
		if user_id in await self.get_grinders():
			await self.bot.db.execute("UPDATE grinder_payments SET tier = ?, perks_allowed = ? WHERE user_id = ?", (tier, perks_allowed, user_id))
		else:
			await self.bot.db.execute("INSERT INTO grinder_payments VALUES(?, ?, ?, ?, ?, ?)", (user_id, perks_allowed, time.time(), 0, 0, tier))
		await self.bot.db.commit()

	async def get_info(self, user_id: int):
		cursor = await self.bot.db.execute("SELECT perks_allowed, start_time, total_paid, paid_in_timeframe, tier FROM grinder_payments WHERE user_id = ?", (user_id, ))
		info = await cursor.fetchone()
		return info

	async def get_grinders(self):
		cursor = await self.bot.db.execute("SELECT user_id FROM grinder_payments")
		info = await cursor.fetchall()
		return [i[0] for i in info]
	
	async def get_all_payments(self):
		h = await self.bot.db.execute("SELECT user_id, paid_in_timeframe, tier FROM grinder_payments")
		return [(a, b, c) for a, b, c in await h.fetchall()]
	
	async def get_ranking_weekly(self, user_id: int) -> int:
		h = await self.bot.db.execute("SELECT user_id, paid_in_timeframe FROM grinder_payments ORDER BY paid_in_timeframe DESC")
		rankings_dict = {a:b for a,b in await h.fetchall()}
		ranking = list(rankings_dict).index(user_id) + 1
		return ranking

	async def get_ranking_monthly(self, user_id: int) -> int:
		h = await self.bot.db.execute("SELECT user_id, total_paid FROM grinder_payments ORDER BY total_paid DESC")
		rankings_dict = {a:b for a,b in await h.fetchall()}
		ranking = list(rankings_dict).index(user_id) + 1
		return ranking
	
	async def get_top_10_weekly(self):
		h = await self.bot.db.execute("SELECT user_id, paid_in_timeframe FROM grinder_payments ORDER BY paid_in_timeframe DESC LIMIT 10")
		return {a:b for a,b in await h.fetchall()}
	
	async def get_top_10_lifetime(self):
		h = await self.bot.db.execute("SELECT user_id, total_paid FROM grinder_payments ORDER BY total_paid DESC LIMIT 10")
		return {a:b for a,b in await h.fetchall()}

class ClaimDatabaseHandler():
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		self.bot.loop.create_task(self.startup())

	async def startup(self):
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS claims (user_id bigint, whatfor text, prize text, time bigint)")
		await self.bot.db.commit()

	async def add(self, user_id, whatfor: Literal["counting"], prize):
		await self.bot.db.execute("INSERT INTO claims VALUES(?, ?, ?, ?)", (user_id, whatfor, prize, time.time()))
		await self.bot.db.commit()

	async def get_prize(self, user_id, whatfor):
		cursor = await self.bot.db.execute("SELECT prize FROM claims WHERE user_id = ? AND whatfor = ?", (user_id, whatfor))
		info = await cursor.fetchall()
		return [i[0] for i in info]
	
	async def rem(self, user_id, whatfor, prize):
		await self.bot.db.execute("DELETE FROM claims WHERE user_id = ? AND whatfor = ? AND prize = ?", (user_id, whatfor, prize))
		await self.bot.db.commit()


class AllowancesDatabaseHandler():
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.loop.create_task(self.startup())

	async def startup(self):
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS allowances (user_id bigint UNIQUE PRIMARY KEY, allowance bigint)")
		await self.bot.db.commit()

	async def get_users(self):
		cursor = await self.bot.db.execute("SELECT user_id FROM allowances")
		info = await cursor.fetchall()
		return [i[0] for i in info]

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
		await self.bot.db.commit()

	async def remove(self, user_id, amount): # amount is the new amount of allowances- not the amount to remove
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
			await self.bot.db.commit()
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

	async def get(self, count: int):
		cursor = await self.bot.db.execute("SELECT user_id, time FROM counting_prizes_log WHERE count = ?", (count, ))
		info = await cursor.fetchone()
		return info

	async def get_all(self):
		cursor = await self.bot.db.execute("SELECT count, user_id, time FROM counting_prizes_log")
		info = await cursor.fetchall()
		return info


class AFKDatabaseHandler:
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		self.bot.loop.create_task(self.startup())
	
	async def startup(self):
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS afk (user_id bigint UNIQUE PRIMARY KEY, msg text, time real)")
		await self.bot.db.commit()

	async def get_afk_users(self):
		return [i[0] for i in await (await self.bot.db.execute("SELECT user_id FROM afk")).fetchall()]

	async def get_afk_message(self, id: int):
		data_raw = await self.bot.db.execute(f"SELECT msg, time FROM afk WHERE user_id = ?", (id,))
		data = await data_raw.fetchone()
		return data

	async def write_afk(self, id: int, message: str, time: float) -> None:
		await self.bot.db.execute("INSERT OR REPLACE into afk (user_id, msg, time) VALUES(?, ?, ?)", (id, message, time, ))
		await self.bot.db.commit()

	async def remove_afk(self, id: int) -> None:
		await self.bot.db.execute("DELETE FROM afk WHERE user_id = ?", (id, ))
		await self.bot.db.commit()

	async def go_afk(self, user_id, message: str, time: float):
		await self.write_afk(user_id, message, time)


class RemindersDatabaseHandler:
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		self.bot.loop.create_task(self.startup())

	async def startup(self):
		await self.bot.db.execute("CREATE TABLE IF NOT EXISTS reminders (ind bigint, user_id bigint, message text, time bigint, channel bigint, message_id bigint)")
		await self.bot.db.commit()

	async def get_reminders(self, user_id):
		cur = await self.bot.db.execute("SELECT * FROM reminders WHERE user_id = ? ORDER BY ind", (user_id, ))
		return await cur.fetchall()

	async def get_all(self):
		cur = await self.bot.db.execute("SELECT * FROM reminders")
		return await cur.fetchall()

	async def add(self, index, user_id, message, time, channel, message_id):
		await self.bot.db.execute("INSERT INTO reminders VALUES(?, ?, ?, ?, ?, ?)", (index, user_id, message, time, channel, message_id))
		await self.bot.db.commit()

	async def rem(self, user_id, message_id):
		await self.bot.db.execute("DELETE FROM reminders WHERE user_id = ? and message_id = ?", (user_id, message_id))
		await self.bot.db.commit()
	
	async def purge_user(self, user_id):
		await self.bot.db.execute("DELETE FROM reminders WHERE user_id = ?", (user_id, ))
		await self.bot.db.commit()
