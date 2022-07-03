"""Configurations Used:
counting_channel         int    - The channel in which the bot listens for counting messages
counting_count           int    - The last count the bot knows of
counting_count_author    int    - The author of the last count
counting_prizes          dict[str, str] = Dict of prizes to be paid out in counting
prize_claim_channel_id   int    - The channel in which the bot says the prizes are given
"""
from nextcord.ext.commands import Cog, Bot
from nextcord import Message
import re
pattern = re.compile("\d+")



class Counting(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_message")
    async def on_message_counting(self, message: Message):
        if message.author.bot:
            return
        if message.channel.id != self.bot.config.get("counting_channel"):
            return
        if not message.content.isdigit():
            await message.add_reaction("<:MC_Scam:842301764275535893>")
            return

        count = int(message.content)

        if count != self.bot.config.get("counting_count") + 1:
            await message.delete()
            await message.channel.send(
                content=f"Incorrect count, try again! Imagine not knowing how to count, smh.\n(If you think there is a problem, please contact <@{self.bot.owner_id}>.)",
                delete_after=10)
            return

        if message.author.id == self.bot.config.get("counting_count_author"):
            await message.delete()
            await message.channel.send(
                content=f"You are not allowed to count twice in a row, smh.\n(If you think there is a problem, please contact <@{self.bot.owner_id}>.)",
                delete_after=10)
            return

        self.bot.config.update("counting_count", count)
        self.bot.config.update("counting_count_author", message.author.id)
        await message.add_reaction("☑️")

        if message.content not in self.bot.config.get("counting_prizes"):
            return
        await message.channel.send(f"""
Congrats {message.author.mention}! You won **{self.bot.config.get('counting_prizes')[message.content]}**!
Please open a support thread to claim your prize. <#{self.bot.config.get('prize_claim_channel_id')}>
""")

def setup(bot: Bot):
    bot.add_cog(Counting(bot))

