"""Configurations Used:
wait_for_timeout     int - The amount of time the bot waits for a message before closing a support thread
support_role         int - The role that is pinged to assist in threads
support_channel_id   int - The channel id in which the support menu is sent and users are redirected to for help
"""

from asyncio import TimeoutError
from typing import Optional
from datetime import date
from nextcord.ext import commands
from nextcord import (
    Button,
    ButtonStyle,
    ChannelType,
    Colour,
    Embed,
    Forbidden,
    HTTPException,
    Interaction,
    Member,
    MessageType,
    Thread,
    ThreadMember,
    Message,
    ui,
    User,
    AllowedMentions,
)


async def get_thread_author(channel: Thread) -> Member:
    history = channel.history(oldest_first = True, limit = 1)
    history_flat = await history.flatten()
    user: User = history_flat[0].mentions[0]
    return user


async def close_support_thread(thread_channel: Thread, thread_author: User, bot) -> None:
    if bot.support_users[thread_author.id] == 1:
        del bot.support_users[thread_author.id]
    else:
        bot.support_users[thread_author.id] -= 1

    """
    Closes a support thread. Is called from either the close button or the
    `db close` command.
    """

    # no need to do any of this if the thread is already closed.
    if (thread_channel.locked or thread_channel.archived):
        return

    if not thread_channel.last_message or not thread_channel.last_message_id:
        _last_msg: Optional[Message] = (await thread_channel.history(limit = 1).flatten())[0]
    else:
        _last_msg: Message = thread_channel.get_partial_message(thread_channel.last_message_id)

    thread_jump_url: str = _last_msg.jump_url

    embed_reply: Embed = Embed(title="This thread has now been closed",
                        description=f"To view the contents of this thread again, you may visit the [link]({thread_jump_url}) sent to your DMs.\n For further assistance, please feel free to open another thread!",
                        colour=0xfffa65).set_footer(icon_url=thread_author.display_avatar.url, text="DB Bot | Glad we could help.").set_thumbnail(url=thread_channel.guild.icon.url)

    await thread_channel.send(embed=embed_reply)  # Send the closing message to the support thread
    await thread_channel.edit(locked = True, archived = True)  # Lock thread

    # Make some slight changes to the previous thread-closer embed
    # to send to the user via DM.
    embed_reply.title = "Your support thread in Dank Business has been closed."
    embed_reply.description = f"You can use [**this link**]({thread_jump_url}) to access the archived thread for future reference"
    if thread_channel.guild.icon:
        embed_reply.set_thumbnail(url=thread_channel.guild.icon.url).set_footer(text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
    try:
        await thread_author.send(embed=embed_reply)
    except (HTTPException, Forbidden):
        pass

class SupportButton(ui.Button["SupportView"]):
    def __init__(self, bot, *, style: ButtonStyle, custom_id: str) -> None:
        self.bot = bot
        super().__init__(label = f"Support", style = style, custom_id = f"db_{custom_id}")

    async def create_support_thread(self, interaction: Interaction) -> Thread:
        if interaction.user.id in self.bot.support_users.keys():
            self.bot.support_users[interaction.user.id] += 1
        else:
            self.bot.support_users[interaction.user.id] = 1

        thread: Thread = await interaction.channel.create_thread(
            name = f"{interaction.user}",
            type = ChannelType.public_thread,
        )

        em: Embed = Embed(
            title = "Support thread",
            colour = Colour.blurple(),
            description = "Please explain your issue with relevant proofs, if applicable.",
        )
        em.set_footer(text = "You can close this thread with the button or the db close command.")

        close_button_view = ThreadCloseView(self.bot)

        msg: Message = await thread.send(
            content = interaction.user.mention,
            embed = em,
            view = close_button_view
        )

        # it's a persistent view, we only need the button.
        close_button_view.stop()
        await msg.pin(reason = "First message in support thread with the close button.")
        return thread

    async def __launch_wait_for_message(self, thread: Thread, interaction: Interaction) -> None:
        assert self.view is not None

        def is_allowed(message: Message) -> bool:
            return message.author.id == interaction.user.id and message.channel.id == thread.id and not thread.archived  # type: ignore

        try:
            await self.view.bot.wait_for("message", timeout=self.bot.config.get("wait_for_timeout"), check=is_allowed)
        except TimeoutError:
            return await close_support_thread(thread, interaction.user, self.bot)
        else:
            return await thread.send(f"<@&{self.bot.config.get('support_role')}>", delete_after=5)

    async def callback(self, interaction: Interaction) -> None:
        if interaction.user.id in self.bot.support_users.keys():
            if self.bot.support_users[interaction.user.id] >= 2:
                return await interaction.send("You can have at max 3 support threads at once.", ephemeral=True)
        confirm_view = ConfirmView()

        def disable_all_buttons():
            for _item in confirm_view.children:
                _item.disabled = True

        confirm_content: str = f"Are you really sure you want to make an support thread?"

        await interaction.send(content = confirm_content, ephemeral = True, view = confirm_view)
        await confirm_view.wait()

        if confirm_view.value is False or confirm_view.value is None:
            disable_all_buttons()
            content: str = "Ok, cancelled." if confirm_view.value is False else f"~~{confirm_content}~~ I guess not..."
            await interaction.edit_original_message(content = content, view = confirm_view)
        else:
            disable_all_buttons()
            await interaction.edit_original_message(content = "Created!", view = confirm_view)
            created_thread: Thread = await self.create_support_thread(interaction)
            await self.__launch_wait_for_message(created_thread, interaction)


class SupportView(ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout = None)
        self.bot: commands.Bot = bot

        self.add_item(SupportButton(bot, style = ButtonStyle.blurple, custom_id = "support"))

class ConfirmButton(ui.Button["ConfirmView"]):
    def __init__(self, label: str, style: ButtonStyle, *, custom_id: str) -> None:
        super().__init__(label = label, style = style, custom_id = f"db_{custom_id}")

    async def callback(self, interaction: Interaction) -> None:
        self.view.value = True if self.custom_id == f"db_confirm_button" else False
        self.view.stop()


class ConfirmView(ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = 10.0)
        self.value = None
        self.add_item(ConfirmButton("Yes", ButtonStyle.green, custom_id = "confirm_button"))
        self.add_item(ConfirmButton("No", ButtonStyle.red, custom_id = "decline_button"))


class ThreadCloseView(ui.View):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__(timeout = None)

    @ui.button(label = "Close", style = ButtonStyle.red, custom_id = f"db_thread_close")  # type: ignore
    async def thread_close_button(self, button: Button, interaction: Interaction) -> bool:
        button.disabled = True
        await interaction.response.edit_message(view = self)
        thread_author: User = await get_thread_author(interaction.channel)  # type: ignore
        await close_support_thread(interaction.channel, thread_author, self.bot)

    async def interaction_check(self, interaction: Interaction) -> bool:

        # because we aren't assigning the persistent view to a message_id.
        if not isinstance(interaction.channel, Thread) or interaction.channel.parent_id != self.bot.config.get("support_channel_id"):
            return False

        if (interaction.channel.archived or interaction.channel.locked):  # type: ignore
            return False

        thread_author = await get_thread_author(interaction.channel)  # type: ignore
        if interaction.user.id == thread_author.id or interaction.user.get_role(self.bot.config.get("support_role")):  # type: ignore
            return True
        else:
            await interaction.send("You are not allowed to close this thread.", ephemeral=True)
            return False

class SupportCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.loop.create_task(self.create_views())
        bot.support_users = {}
        bot.allowed_users = {}
        bot.disallowed_users = {}

    async def create_views(self) -> None:
        if not self.bot.support_view_set:
            self.bot.support_view_set = True
            self.bot.add_view(SupportView(self.bot))
            self.bot.add_view(ThreadCloseView(self.bot))

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.channel.id == self.bot.config.get("support_channel_id") and message.type is MessageType.thread_created:
            await message.delete(delay = 5)
        if isinstance(message.channel, Thread) and \
                message.channel.parent_id == self.bot.config.get("support_channel_id") and \
                message.type is MessageType.pins_add:
            await message.delete(delay = 10)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member: ThreadMember) -> None:
        thread: Thread = member.thread
        if thread.parent_id != self.bot.config.get("support_channel_id") or thread.archived:
            return

        thread_author = await get_thread_author(thread)
        if member.id != thread_author.id:
            return

        await close_support_thread(thread, thread_author, self.bot)

    @commands.command()
    @commands.is_owner()
    async def support_menu(self, ctx: commands.Context) -> None:
        channel = await self.bot.getch_channel(self.bot.config.get("support_channel_id"))
        await channel.send(
            view=SupportView(self.bot),
            embed=Embed(
                title="Dank Business Support",
                description="""
Click the button below to create a support thread.
Explain your problem/question with relevant links/proofs and a staff member will be with you shortly!""",
                color=Colour.yellow()
            ).
            set_thumbnail(url=ctx.guild.icon.url).
            set_footer(
                text=f"DB Bot | Support System",
                icon_url=self.bot.user.display_avatar.url
            )
        )

    @commands.command()
    async def close(self, ctx: commands.Context) -> None:
        if not isinstance(ctx.channel, Thread) or ctx.channel.parent_id != self.bot.config.get("support_channel_id"):
            return

        first_thread_message: Message = (await ctx.channel.history(limit=1, oldest_first=True).flatten())[0]
        thread_author = first_thread_message.mentions[0]
        if not (ctx.author.id == thread_author.id or ctx.author.get_role(self.bot.config.get("support_role"))):
            return await ctx.send("You are not allowed to change the topic of this thread.")

        thread_author: User = await get_thread_author(ctx.channel)
        await close_support_thread(ctx.channel, thread_author, self.bot)

    @commands.command()
    async def add(self, ctx: commands.Context, user: User) -> None:
        if ctx.guild.get_role(self.bot.config.get("support_role")) not in ctx.author.roles:
            return ctx.reply("You aren't allowed to do that!")

        try:
            self.bot.allowed_users[ctx.channel.id] = self.bot.allowed_users[ctx.channel.id].append(user.id)
        except:
            self.bot.allowed_users[ctx.channel.id] = [user.id]

        try:
            del self.bot.disallowed_users[ctx.channel.id]
        except:
            pass

        await ctx.channel.send(user.mention, delete_after=0)
        await ctx.channel.send(f"\✅ Added {user.mention} to the thread.", allowed_mentions=AllowedMentions.none())

    @commands.command()
    async def remove(self, ctx: commands.Context, user: User) -> None:
        if ctx.guild.get_role(self.bot.config.get("support_role")) not in ctx.author.roles:
            return ctx.reply("You aren't allowed to do that!")
        if ctx.channel.id in self.bot.allowed_users.keys():
            if user.id in self.bot.allowed_users[ctx.channel.id]:
                del self.bot.allowed_users[ctx.channel.id]

        if ctx.channel.id in self.bot.disallowed_users.keys():
            self.bot.disallowed_users[ctx.channel.id] = self.bot.disallowed_users[ctx.channel.id].append(user.id)
        else:
            self.bot.disallowed_users[ctx.channel.id] = [user.id]

        await ctx.channel.remove_user(user)
        await ctx.channel.send(f"\❎ Removed {user.mention} from the thread. They will not be able to join again unlessy you add them.", allowed_mentions=AllowedMentions.none())

    @commands.Cog.listener("on_thread_member_join")
    async def on_thread_member_join(self, member: Member) -> None:
        first_thread_message: Message = (await member.thread.history(limit=1, oldest_first=True).flatten())[0]
        thread_author: User = first_thread_message.mentions[0]
        if member.thread.parent_id != self.bot.config.get("support_channel_id"):
            return
        
        try:
            if member.id in self.bot.disallowed_users[member.thread_id]:
                await member.thread.remove_user(member)
                return
        except:
            pass
        try:
            if member.id in self.bot.allowed_users[member.thread_id]:
                return
        except:
            pass
        if not (member.id == thread_author.id or member.thread.guild.get_member(member.id).get_role(self.bot.config.get("support_role"))):
            await member.thread.remove_user(member)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(SupportCog(bot))
