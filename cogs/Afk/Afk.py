from nextcord.ext import commands
from nextcord import Message
import time
from BotBase import BotBaseBot

class AFK(commands.Cog):
    def __init__(self, bot: BotBaseBot):
        self.bot: BotBaseBot = bot

    @commands.group(invoke_without_command=True)
    async def afk(self, ctx: commands.Context[commands.Bot], *, msg: str ="busy gettin' a life"):
        if len([i for i in self.bot.AfkConfig.get("allowed_roles") if i in [j.id for j in ctx.author.roles]]) == 0 and ctx.author.id not in self.bot.AfkConfig.get("allowed_users"):
            return await ctx.send("You don't have permission to use this command.")

        if "[AFK]" not in ctx.message.author.display_name:
            try:
                await ctx.author.edit(nick=f"{ctx.author.display_name} [AFK]")
            except:
                pass

        await self.bot.afk_db.write_afk(ctx.author.id, msg, time.time())
        await ctx.reply(f"You are now afk with reason: {msg}")


    @commands.Cog.listener("on_message")
    async def on_message_afk(self, msg: Message) -> None:
        if msg.author.bot:
            return
        if msg.channel.id in self.bot.AfkConfig.get("ignored_channels"):
            return

        afk_users = await self.bot.afk_db.get_afk_users()

        if msg.author.id in afk_users:
            if "[AFK]" in msg.author.display_name:
                await msg.author.edit(nick=msg.author.display_name.replace("[AFK]", ""))

            await self.bot.afk_db.remove_afk(msg.author.id)
            await msg.reply("Welcome back from afk!")

        if not msg.mentions:
            return

        temp_message = ""
        for user in msg.mentions:
            if user.id in afk_users:
                afk_reason, afk_since = await self.bot.afk_db.get_afk_message(user.id)
                temp_message = f"{user.name} is afk: {afk_reason} <t:{int(afk_since)}:R>"

        if temp_message == "":
            return
        if len(temp_message) > 2000:
            return await msg.reply("Seriously, mention so many AFK users in a message next time and I'll mute you.")

        await msg.reply(temp_message)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AFK(bot))
