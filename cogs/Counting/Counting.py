"""Configurations Used:
counting_channel         int    - The channel in which the bot listens for counting messages
words_allowed_role       int    - The role that is allowed to send words in the counting channel
counting_count           int    - The last count the bot knows of
counting_count_author    int    - The author of the last count
counting_prizes          dict[str, str] = Dict of prizes to be paid out in counting
prize_claim_channel_id   int    - The channel in which the bot says the prizes are given

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

    @Cog.listener("on_message")
    async def on_message_counting(self, message: Message):
        if message.author.bot:
            return
        if message.channel.id != self.bot.CountingConfig.get("counting_channel"):
            return
        if not message.content.isdigit():
            if message.guild.get_role(self.bot.CountingConfig.get("words_allowed_role")) in message.author.roles:
                return
            await message.add_reaction("<:MC_Scam:842301764275535893>")
            return

        count = int(message.content)

        if count != self.bot.CountingConfig.get("counting_count") + 1:
            await message.delete()
            await message.channel.send(
                content=f"Incorrect count, try again! Imagine not knowing how to count, smh.\n(If you think there is a problem, please contact <@{self.bot.owner_id}>.)",
                allowed_mentions=AllowedMentions.none(),
                delete_after=10)
            return

        if message.author.id == self.bot.CountingConfig.get("counting_count_author"):
            await message.delete()
            await message.channel.send(
                content=f"You are not allowed to count twice in a row, smh.\n(If you think there is a problem, please contact <@{self.bot.owner_id}>.)",
                allowed_mentions=AllowedMentions.none(),
                delete_after=10)
            return

        self.bot.CountingConfig.update("counting_count", count)
        self.bot.CountingConfig.update("counting_count_author", message.author.id)
        await message.add_reaction("☑️")

        if message.content not in self.bot.CountingConfig.get("counting_prizes"):
            return
        mes = await message.channel.send(f"""
Congrats {message.author.mention}! You won **{self.bot.CountingConfig.get('counting_prizes')[message.content]}**!
Please run the command `db claim prize counting <link-to-this-message>` <#{self.bot.CountingConfig.get('prize_claim_channel_id')}>
""")
        await mes.edit(content=mes.content.replace("<link-to-this-message>", mes.jump_url))

        previous_allowances = self.bot.allowances_db.get_allowances(
            message.author.id)
        if previous_allowances is None:
            allowance = 1
        else:
            allowance = previous_allowances + 1

        await self.bot.allowances_db.add(message.author.id, allowance)

    @Cog.listener("on_message_delete")
    async def on_message_counting_delete(self, message: Message):
        if message.channel.id != self.bot.CountingConfig.get("counting_channel"):
            return
        if message.content == self.bot.CountingConfig.get("counting_count"):
            self.bot.CountingConfig.update("counting_count", self.bot.CountingConfig.get("counting_count") - 1)
            await message.channel.send(
                content=f"You dirty little bad kid ruinin it for everyone be deletin your messages. Don't wanna play? ok, here's the event blacklist for you",
                delete_after=10
            )
            await message.author.add_roles(message.guild.get_role(self.bot.CountingConfig.get("events_blacklist_role")))


def setup(bot: Bot):
    bot.add_cog(Counting(bot))

