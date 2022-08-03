from nextcord.ext.commands import Cog, Bot
from nextcord.ext import commands
from nextcord import Embed, Colour


class Perks(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="vote_perks")
    async def vote_perks(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")

        if here is not None:
            channel = await self.bot.getch_channel(self.bot.config.get("vote_perks_channel"))
        else:
            channel = ctx.channel
        
        embed=Embed(
            title="Voter Benefits!",
            description=f"""
Voting for this server will get you the followwing!**
> > <@&{self.bot.config.get("voter_role")}> Role
> > 2x Amari Everywhere!
> > Exclusive Giveaways!

Click [here](https://top.gg/servers/819084505037799465/vote)** for the voting link! (https://top.gg/servers/819084505037799465/vote)

To check the leaderboard, run `=lb` in <#990096799899475978>
""",        colour=0xfffa65
        ).set_footer(text="Thanks for keeping the server great!").set_thumbnail(url=self.bot.user.display_avatar.url)

        await channel.send(embed=embed)

    @commands.command(name="booster_perks")
    async def booster_perks(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")

        if here is not None:
            channel = await self.bot.getch_channel(self.bot.config.get("booster_perks_channel"))
        else:
            channel = ctx.channel

        embed=Embed(
            title="Booster Perks!",
            description=f"""
<a:MC_boost:819689268112916481> **SINGLE BOOSTER PERKS**
<a:MC_TDT_arrow2:845416602869432340> <@&{self.bot.config.get("booster_roles")["single"]}> role
<a:MC_TDT_arrow2:845416602869432340> **Exclusive Giveaways**
<a:MC_TDT_arrow2:845416602869432340> Granted `db afk` command
<a:MC_TDT_arrow2:845416602869432340> Granted Premium colour roles
═════════════
<a:MC_boost:819689268112916481> **DOUBLE BOOSTER PERKS**
<a:MC_TDT_arrow2:845416602869432340> All perks above +
<a:MC_TDT_arrow2:845416602869432340> <@&{self.bot.config.get("booster_roles")["double"]}> role
<a:MC_TDT_arrow2:845416602869432340> **Bypass all giveaways**
<a:MC_TDT_arrow2:845416602869432340> Granted `^snipe` command
<a:MC_TDT_arrow2:845416602869432340> +1 auto-reaction
<a:MC_TDT_arrow2:845416602869432340> Office with up to 7 friends!
═════════════
<a:MC_boost:819689268112916481> **TRIPLE BOOSTER PERKS**
<a:MC_TDT_arrow2:845416602869432340> All perks above +
<a:MC_TDT_arrow2:845416602869432340> <@&{self.bot.config.get("booster_roles")["triple"]}> role
<a:MC_TDT_arrow2:845416602869432340> +1 auto-reaction
<a:MC_TDT_arrow2:845416602869432340> +7 friends in your office

""",        colour=0xfffa65
        ).set_footer(text="Thanks for keeping the server great!").set_thumbnail(url=self.bot.user.display_avatar.url)

        await channel.send(embed=embed)

    @commands.command(name="level_perks")
    async def level_perks(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")

        if here is not None:
            channel = await self.bot.getch_channel(self.bot.config.get("perks_channel"))
        else:
            channel = ctx.channel

        embed=Embed(
            title="Level Rewards!",
            description=f"""
<@&{self.bot.config.get("level_roles")["10"]}>
➥ **Exclusive Giveaways**
➥ Granted `^snipe` command
<@&{self.bot.config.get("level_roles")["20"]}>
➥ Granted `db afk` command
<@&{self.bot.config.get("level_roles")["30"]}>
➥ Granted image in <#{self.bot.config.get("main_chat")}>
# <@&{self.bot.config.get("level_roles")["40"]}>
➥ +1 auto reaction
<@&{self.bot.config.get("level_roles")["50"]}>
➥ Premium colour roles
<@&{self.bot.config.get("level_roles")["69"]}>
➥ Unique role & hex
➥ Access to President's Office & info
<@&{self.bot.config.get("level_roles")["100"]}>
➥ ||I guess you'll never know||
""",        colour=0xfffa65
        ).set_footer(text="Thanks for keeping the server great!").set_thumbnail(url=self.bot.user.display_avatar.url)

        await channel.send(embed=embed)

    @commands.command(name="donator_perks")
    async def donator_perks(self, ctx: commands.Context, here=None):
        if not (ctx.author.guild_permissions.manage_guild or ctx.author.id == self.bot.owner_id):
            return await ctx.send("Only guild managers are allowed to use this command.")

        if here is not None:
            channel = await self.bot.getch_channel(self.bot.config.get("perks_channel"))
        else:
            channel = ctx.channel

        embed=Embed(
            title="Donator Perks!",
            description=f"""
<@&{self.bot.DonoConfig.get("dono_roles")["5000000"]}>
➥ Donator channel [Amari x2]
<@&{self.bot.DonoConfig.get("dono_roles")["69000000"]}>
➥ Granted `db afk` command
<@&{self.bot.DonoConfig.get("dono_roles")["100000000"]}>
➥ Granted reactions in <#{self.bot.config.get("main_chat")}> 
<@&{self.bot.DonoConfig.get("dono_roles")["250000000"]}>
➥ Presidential Acknowledgement
<@&{self.bot.DonoConfig.get("dono_roles")["500000000"]}>
➥ Message Logs
<@&{self.bot.DonoConfig.get("dono_roles")["750000000"]}>
➥ Granted auto-reaction of choice
<@&{self.bot.DonoConfig.get("dono_roles")["1000000000"]}>
➥ Billionaire channel [Amari x3]
<@&{self.bot.DonoConfig.get("dono_roles")["2500000000"]}>
➥ Granted unique role
<@&{self.bot.DonoConfig.get("dono_roles")["5000000000"]}>
➥ Granted unique hexcode
""",        colour=0xfffa65
        ).set_footer(text="Thanks for keeping the server great!").set_thumbnail(url=self.bot.user.display_avatar.url)

        await channel.send(embed=embed)

def setup(bot: Bot):
    bot.add_cog(Perks(bot))
