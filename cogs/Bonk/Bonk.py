from nextcord import User, Embed, Message
from nextcord.ext import commands
from cogs.utils import convert_time
import time

class Bonk(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    async def remind(self, user_id: int, channel_id, message_id, message: str = None) -> None:
        await self.bot.reminders_db.rem(user_id, message_id)
        user: User = await self.bot.getch_user(user_id)

        ms: Message = await self.bot.getch_message(channel_id, message_id)
        if ms:
            jump_url = ms.jump_url
            message = message or jump_url or "Unknown"
            await ms.reply(f"Reminder!")
            return

        try:
            return await user.send(f"Reminder for `{message}`")
        except:
            owner = await self.bot.getch_user(self.bot.owner_id)
            await owner.send(f"Unable to send reminder to {user.mention}, message: `{message}`")
        
        reminders = await self.bot.reminders_db.get_reminders(user.id)
        await self.bot.reminders_db.purge_user(user.id)

        if not reminders:
            return
        else:
            for i in reminders:
                reminders[0] = i+1
                await self.bot.reminders_db.add(reminders[0], reminders[1], reminders[2], reminders[3], reminders[4])

    @commands.group(invoke_without_command=True, name="bonk", aliases=["remindme", "remind"])
    async def _bonk(self, ctx: commands.Context, duration: str, *, message: str = None) -> None:

        duration = convert_time(duration)

        if duration is False:
            return await ctx.send("Invalid time format.")
        if duration > 60*60*24*7*2:
            return await ctx.send("You can't set a reminder for more than 2 weeks.")

        end_time = time.time()+duration

        rems = await self.bot.reminders_db.get_reminders(ctx.author.id)

        if len(rems) == 0:
            index = 1
        else:
            index = rems[-1][0]+1

        await self.bot.reminders_db.add(index, ctx.author.id, message, end_time, ctx.channel.id, ctx.message.id)

        self.bot.loop.call_later(
            duration, 
            lambda: self.bot.loop.create_task(self.remind(ctx.author.id, ctx.channel.id, ctx.message.id, message, )))

        m = f"about `{message}` " if message else ""
        await ctx.send(f"I'll remind you {m}on <t:{int(end_time)}:F>")

    @commands.command(name="bonks", aliases=["reminders", "all", "list"])
    async def _bonks(self, ctx: commands.Context) -> None:
        rems = await self.bot.reminders_db.get_reminders(ctx.author.id)
        print(rems)

        if len(rems) == 0:
            return await ctx.reply("You have no reminders.")

        res = []
        for i in range(len(rems)):
            j = f"`{rems[i][0]}.` Set on: <t:{int(rems[i][3])}:F> [{rems[i][2]}](https://discord.com/channels/819084505037799465/{rems[i][4]}/{rems[i][5]})"
            print(j)
            res.append(j)
        res = "\n".join(res)
        await ctx.send(
            embed=Embed(
                title="Your Reminders",
                description=res
            ).set_thumbnail(url=ctx.guild.icon.url).set_footer(text=f"DB Bot | Reminders")
        )

    @_bonk.command(name="remove", aliases=["delete", "remonvereminder", "remove_reminder"])
    async def _remove_reminder(self, ctx: commands.Context, index: int):
        rems = await self.bot.reminders_db.get_reminders(ctx.author.id)

        if index > len(rems):
            return await ctx.reply("You don't have that many reminders!")

        message_id = rems[index-1][5]
        await self.bot.reminders_db.rem(ctx.author.id, message_id)

        await ctx.reply("Removed reminder.")

    @commands.Cog.listener("on_ready")
    async def _bonk_on_ready(self) -> None:
        rems = await self.bot.reminders_db.get_all()

        for reminder in rems:
            end_time = reminder[3]
            if time.time() < end_time:
                time_left = end_time - time.time()
                rem = self.bot.loop.call_later(time_left, self.remind(reminder[1], reminder[4], reminder[5], reminder[2]))
            else:
                await self.remind(reminder[1], reminder[4], reminder[5], reminder[2])

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Bonk(bot))
