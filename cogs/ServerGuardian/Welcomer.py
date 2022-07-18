from datetime import timedelta
import nextcord
from nextcord.ext import commands
import datetime


class ServerGuardian(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.freeloader_role = self.bot.treasury.get_role(762301816552554496)
        self.staff_role = self.bot.treasury.get_role(self.bot.STAFF_ID)

    async def unquarantine(self, member_id: int) -> None:
        member = await self.bot.getch_member(self.bot.treasury.id, member_id)
        if not member:
            return
        await member.remove_roles(self.bot.quarantine_role)

    @commands.Cog.listener("on_member_join")
    async def join_ghost_ping_(self, member):
        await member.add_roles(self.freeloader_role)
        await self.bot.ghost_ping_channel.send(member.mention, delete_after=0)
        try:
            await member.send(
                embed=nextcord.Embed(
                    title="Welcome to The Treasury!",
                    colour=0x00ffea,
                    description=f"""
Welcome to The Dank Treasury {member.mention}! Glad to have you with us!
We suggest going through our [rules](https://discord.com/channels/727276010600530011/727279259932164196) before anything else.
And then getting some [self roles](https://discord.com/channels/727276010600530011/730800446251204689) for yourself- to access channels and get pinged on various events!
If the sad event that you get banned, you can appeal [here](https://{self.bot.appeal_guild_invite})
                    """
                ).set_footer(
                    text="TreasuryBot",
                    icon_url=self.bot.user.avatar.url
                ).set_thumbnail(
                    url=self.bot.treasury.icon.url
                )
            )
        except:
            pass

    @commands.command(name="qinfo")
    @commands.is_owner()
    async def quarantine_info_embed_(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        embed = nextcord.Embed(
            title="Why are you here? <a:TDT_PepeSadge:948535177792069663>",
            description="""
<:TDT_cyanbow:943559940583329833> **__Why do I have this role??__ ** <a:TDT_Think:948533371749945354>
<a:TDT_arrow4:944983882921549824> Instead of kicking/temp-banning new accounts (i.e. account younger than 15 days) in our server, we give them the <@&946695635816579072> instead. This puts them in a quarantined area away from the server.
<a:TDT_arrow4:944983882921549824> If you have previously been banned, you will be placed here until you reach level 20.
<:TDT_cyanbow:943559940583329833>: How can I get rid of this role? <a:TDT_nyaThinking:948532755166294036>
<a:TDT_arrow4:944983882921549824> If you are a new account, this role will automatically be removed whenever your account is over 15 days old and you can access all other channels in the server thereafter.
<a:TDT_arrow4:944983882921549824> If you have previously been banned, you can ask a mod to remove it once you reach level 20 >r
<:TDT_cyanbow:943559940583329833> What can I do in the meanwhile? <:TDT_WorryThink:948533026520977409>
<a:TDT_arrow4:944983882921549824> You can access Dank Memer in <#948280091463532564> and <#948280154612981780> and all other bots in <#948280640854446141> which are channels for quarantined people.
""",
            color=0x00ffea,
        ).set_thumbnail(url=ctx.guild.icon.url).set_footer(text="TreasuryBot", icon_url=ctx.guild.me.display_avatar.url)
        await self.bot.quarantine_info_channel.send(embed=embed)

    @commands.Cog.listener("on_member_join")
    async def member_quaratine(self, member: nextcord.Member) -> None:
        if member.created_at > nextcord.utils.utcnow() - timedelta(days=15):
            await member.add_roles(self.bot.quarantine_role)
            await member.remove_roles(*member.roles)
            remove_time = datetime.datetime.timestamp(datetime.datetime.utcnow(
            ) + datetime.timedelta(seconds=datetime.timedelta(days=15)-member.created_at))

            self.bot.db.execute(
                "INSERT INTO quarantine (user_id, time) VALUES (?, ?)", (member.id, remove_time, ))
            self.bot.loop.call_later(remove_time, self.unquarantine(member.id))

            try:
                await member.send(
                    f"""
                    You have been quarantined in `The Treasury` for your account being **too new**.
                    This will **automatically** be removed once your account **reaches 15 days of age**.
                    For further inquiries or raising a special exception case, please join and contact our support tema at **{self.bot.appeal_guild_invite}**.
                    """
                )
            except:
                pass
            await self.bot.quarantine_info_channel.send(member.mention, delete_after=0)

    @commands.Cog.listener("on_ready")
    async def unquarantine_on_ready_(self):
        unquarantines = await self.bot.db.execute("SELECT * FROM quarantine")
        unquarantines = await unquarantines.fetchall()

        for unquarantine in unquarantines:
            seconds = (datetime.datetime.utcnow(
            ) - datetime.datetime.fromtimestamp(unquarantine[1])).total_seconds()
            self.bot.loop.call_later(seconds, self.unquarantine(
                unquarantines[0], unquarantines[1]))

    @commands.Cog.listener("on_message")
    async def on_message_auto_delete(self, message):
        if message.channel.id == 727279004385804378 and message.attachments and self.staff_role not in message.author.roles:
            await message.delete()


def setup(bot):
    bot.add_cog(ServerGuardian(bot))
