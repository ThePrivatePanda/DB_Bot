"""Configurations Used:
CountingConfig -
    counting_channel         int    - The channel in which the bot listens for counting messages
    words_allowed_role       int    - The role that is allowed to send words in the counting channel
    counting_count           int    - The last count the bot knows of
    counting_count_author    int    - The author of the last count
    counting_prizes          dict[str, str] = Dict of prizes to be paid out in counting
    prize_claim_channel_id   int    - The channel in which the bot says the prizes are given
    events_blacklist_role    int    - Role given when someone deletes their count

Config -
    support_channel          int    - Channel in which user is redirected to appeal his event ban

DB stuff used:
AllowancesDatabase: how many times a person can claim!
"""

from nextcord.ext.commands import Cog, Bot
from nextcord import Message, AllowedMentions
import re
pattern = re.compile("\d+")



class Counting(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.managed = []

    @Cog.listener("on_message")
    async def on_message_counting(self, message: Message):
        if message.author.bot:
            return
        if message.channel.id != self.bot.CountingConfig.get("counting_channel"):
            return
        if not message.content.isdigit():
            if message.guild.get_role(self.bot.CountingConfig.get("words_allowed_role")) in message.author.roles:
                return
            await message.delete()
            return

        count = int(message.content)

        if count != self.bot.CountingConfig.get("counting_count") + 1:
            self.managed.append(message.id)
            await message.delete()
            await message.channel.send(
                content=f"{message.author.mention} Incorrect count, try again! If there's a problem, contact <@{self.bot.owner_id}>.",
                allowed_mentions=AllowedMentions.none(),
                delete_after=5)
            return

        if message.author.id == self.bot.CountingConfig.get("counting_count_author"):
            self.managed.append(message.id)
            await message.delete()
            await message.channel.send(
                content=f"{message.author.mention} You cannot count twice in a row! If there's a problem, contact <@{self.bot.owner_id}>.",
                allowed_mentions=AllowedMentions.none(),
                delete_after=5)
            return

        self.bot.CountingConfig.update("counting_count", count)
        self.bot.CountingConfig.update("counting_count_author", message.author.id)
        await message.add_reaction("☑️")

        if message.content not in self.bot.CountingConfig.get("counting_prizes"):
            return

        await message.channel.send(f"""
Congrats {message.author.mention}! You won **{self.bot.CountingConfig.get('counting_prizes')[message.content]}**!
Please run the command `/claim prize counting` in <#{self.bot.CountingConfig.get('prize_claim_channel_id')}> for the payout!
""")

        previous_allowances = await self.bot.allowances_db.get_allowances(message.author.id)

        if previous_allowances is None:
            allowance = 1
        else:
            allowance = previous_allowances[0] + 1

        await self.bot.allowances_db.add(message.author.id, allowance)
        await self.bot.claims_db.add(message.author.id, "counting", self.bot.CountingConfig.get("counting_prizes")[message.content])


    @Cog.listener("on_message_delete")
    async def on_message_counting_delete(self, message: Message):
        if message.channel.id != self.bot.CountingConfig.get("counting_channel"):
            return
        if message.id in self.managed:
            return
        if message.content == str(self.bot.CountingConfig.get("counting_count")):
            self.bot.CountingConfig.update("counting_count", self.bot.CountingConfig.get("counting_count") - 1)
            await message.channel.send(
                content=f"{message.author.mention} You naughty lil kid ruinin it for everyone be deletin your messages. Don't wanna play? ok, here's the event blacklist for you.",
                delete_after=5
            )

            try:
                await message.channel.send(f"{message.author.mention} Imagine trying to ruin the count.")
            except:
                pass


def setup(bot: Bot):
    bot.add_cog(Counting(bot))

