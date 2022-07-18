from nextcord.ext.commands import Bot, Cog
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, Embed
from DatabaseHandlers import ClaimDatabaseHandler


class Claim(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.claims_db: ClaimDatabaseHandler = ClaimDatabaseHandler(bot)

    @commands.command(name="claim")
    async def claim_main(self): ...

    @claim_main.command(name="prize")
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
        allowances = self.bot.allowances_db.get_allowances(interaction.user.id)

        if allowances is None:
            return await interaction.send(f"Are you sure you have a pending payout? If you think there is a fault, please contact <@{self.bot.owner_id}>.")

        if event == "counting":
            channel = await self.bot.CountingConfig.get("prize_claim_channel_id")
            prizes = await self.bot.claims_db.get_prize(interaction.user.id, "counting")
            if len(prizes) > 1:
                payout = ", ".join([f'{i:3,}' for i in prizes])
            else:
                payout = f"{prizes[0]:3,}"
            await channel.send(
                content=f"<@&{self.bot.config.get('event_manager_role')}> Please attend to this payout for <@{interaction.user.id}>!",
                embed=Embed(
                    title="Prize Claim",
                    description=f"""
User: {interaction.user.mention}
Payout(s): {payout}
Event: Counting
""",
                    color=0x2ecc71
                ).set_thumbnail(url=interaction.guild.icon.url).set_footer(text=f"DB Bot | Prize Claims")
            )

def setup(bot):
    bot.add_cog(Claim(bot))