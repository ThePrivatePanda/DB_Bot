from nextcord.ext.commands import Bot
import asyncio


class GrinderDatabaseHandler():
    def __init__(self, bot: Bot):
        self.bot = bot
        asyncio.run(self.startup())

    async def startup(self):
        await self.bot.db.execute("CREATE TABLE IF NOT EXISTS grinder_payments (user_id bigint UNIQUE PRIMARY KEY, total_paid bigint, paid_in_timeframe bigint, tier bigint)")

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

  
    async def get_info(self, user_id: int):
        cursor = await self.bot.db.execute("SELECT total_paid, paid_in_timeframe, tier FROM grinder_payments WHERE user_id = ?", (user_id, ))
        tier = await cursor.fetchone()
        return tier
