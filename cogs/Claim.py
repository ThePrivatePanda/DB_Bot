from curses.ascii import isdigit
from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, Embed
from DatabaseHandlers import ClaimDatabaseHandler


class Claim(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.claims_db: ClaimDatabaseHandler = ClaimDatabaseHandler(bot)

    @slash_command(name="claim", guild_ids=[819084505037799465])
    async def claim_main(self): ...

    @claim_main.subcommand(name="prize")
    async def claim_prize(
        self,
        interaction: Interaction,
        event: str = SlashOption(
            description="Which event did you win the prize for?",
            required=True,
            choices={
                "Counting": "counting",
            }
        )
    ):
        allowances = await self.bot.allowances_db.get_allowances(interaction.user.id)

        if allowances is None:
            return await interaction.send(f"Are you sure you have a pending payout? If you think there is a fault, please contact <@{self.bot.owner_id}>.", ephemeral=True)

        if event == "counting":
            channel = await self.bot.getch_channel(self.bot.CountingConfig.get("prize_claim_channel_id"))
            prizes = await self.bot.claims_db.get_prize(interaction.user.id, "counting")
            if len(prizes) > 1:
                l = []
                for prize in prizes:
                    await self.bot.claims_db.rem(interaction.user.id, "counting", prize)
                    try:
                        l.append(f"{int(prize):3,}")
                    except:
                        l.append(prize)
                pay = ", ".join(l)
            else:
                await self.bot.claims_db.rem(interaction.user.id, "counting", prize)
                try:
                    pay = f"{int(prizes[0]):3,}"
                except:
                    pay = prizes[0]
            await channel.send(
                content=f"<@&{self.bot.config.get('event_manager_role')}> Please tend to this payout for <@{interaction.user.id}>!",
                embed=Embed(
                    title="Prize Claim",
                    description=f"""
User: {interaction.user.mention}
Payout(s): {pay}
Event: Counting
""",
                    color=0x2ecc71
                ).set_thumbnail(url=interaction.guild.icon.url).set_footer(text=f"DB Bot | Prize Claims")
            )

        await interaction.send(f"You have claimed your prize for {event}! Please wait patiently for the payout, you may use the remind button on the embed once every 4 hours incase there is no payment.", ephemeral=True)
        await self.bot.allowances_db.remove(interaction.user.id, allowances[0]-len(prizes))


def setup(bot):
    bot.add_cog(Claim(bot))