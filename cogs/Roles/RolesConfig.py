from nextcord.ext.commands import Cog, Bot
from nextcord.ext import commands
from nextcord import slash_command, Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel


class RolesConfig(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @slash_command(name="config_selfroles", guild_ids=[819084505037799465], description="Configure various settings of the bot related to slash/self roles.")
    async def config_selfroles(self): ...

    @config_selfroles.subcommand(name="channel", description="Change the channel in which selfrole messages appear. Instant changes.")
    async def config_selfroles_channel(
        self,
        interaction: Interaction,
        new_channel_: GuildChannel = SlashOption(
            channel_types=[ChannelType.text],
            description="The new channel in which selfrole messages will appear",
            required=True
        )
    ):
        old_channel = self.bot.SelfRolesConfig.get("selfroles_channel")
        try:
            await new_channel_.send("Ensuring I can send messages here since I'm too lazy to actually do it through permissions properly.", delete_after=0)
        except Exception as e:
            return await interaction.send(f"An error occured!\n{e}")
        
        for message in self.bot.get_channel(old_channel).history(limit=1000):
            if message.author.id == self.bot.user.id:
                await message.delete()
        self.bot.SelfRolesConfig.update("selfroles_channel", new_channel_.id)

        self.bot.invoke(self.bot.get_command("selfrole colour"), interaction=interaction)




def setup(bot: Bot):
    bot.add_cog(RolesConfig(bot))