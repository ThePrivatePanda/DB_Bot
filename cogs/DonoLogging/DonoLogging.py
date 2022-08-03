from nextcord.ext import commands
from nextcord import Member, Embed, Colour, slash_command, Interaction, SlashOption
from typing import Optional
from cogs.utils import convert_amount

class DonoLogging(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.bot.auto_dono_roles = self.auto_dono_roles

	async def auto_dono_roles(self, member: Member, amount):
		eligible_roles = [role for role in member.guild.roles if role.id in [int(j) for i, j in self.bot.DonoConfig.get('dono_roles').items() if i <= str(amount)]]
		old_roles = [i for i in member.roles if i.id in self.bot.DonoConfig.get("dono_roles").values()]
		r = [i for i in member.roles if i not in old_roles]
		new_roles = r+eligible_roles
		await member.edit(roles=new_roles)

	@slash_command(name="dono", guild_ids=[819084505037799465])
	async def dono_main(self, ctx): ...

	@dono_main.subcommand(name="add")
	async def dono_add(
		self,
		interaction: Interaction, 
		purpose: str = SlashOption(
			description="The purpose of the dono",
			required=True,
			choices={
				"giveaways": "giveaway",
				"special": "special",
				"events": "event",
				"heists": "heist"
			}
		),
		user: Member = SlashOption(
			description="The user to add to the dono",
			required=True
		),
		amount = SlashOption(
			description="The amount of cash to add",
			required=True
		),
		note: str = SlashOption(
			description="An optional note to take regarding this donoation",
			required=False
		)
	):
		...
		if interaction.user.id not in self.bot.DonoConfig.get("managers"):
			return await interaction.send("You are not authorized to do that!", ephemeral=True)

		amount = amount.replace(",", "")
		try:
			amount = convert_amount(amount)
		except:
			return await interaction.send("Invalid amount!", ephemeral=True)

		if amount < 1:
			return await interaction.send("Amount must be more than `1`", ephemeral=True)
		if amount > 5000000000:
			return await interaction.send("You can't add that much at once 💀", ephemeral=True)

		dono_before = await self.bot.dono_db.get_dono(user.id, purpose)
		await self.bot.dono_db.add(user.id, purpose, amount)

		auto_roles = await self.bot.auto_dono_roles(user, dono_before+amount)

		await interaction.send(embed=Embed(
			title="Donation Logged",
			description=f"{user.mention}'s donation of **⏣ {amount:3,}** has been added successfully!\nTotal donations for {purpose}: **⏣ {(dono_before + amount):3,}**\n{'The dono roles have been updated automatically!' if auto_roles else ''}",
			color=Colour.green()
			).set_thumbnail(url=interaction.guild.icon.url).set_footer(text="DB Bot | Donations", icon_url=self.bot.user.display_avatar.url))
		

		dono_log_channel = await self.bot.getch_channel(self.bot.DonoConfig.get("dono_log_channel"))
		if not dono_log_channel:
			return
		await dono_log_channel.send(embed=Embed(
			title="Donation Added",
			description=f"""
Action by: {interaction.user.mention}
User: {user.mention}
Amount Added: **⏣ {amount}**
Bank: {purpose}
Note: {note}
""",
			color=Colour.green()
		).set_thumbnail(url=interaction.guild.icon.url).set_footer(text="DB Bot | Donations", icon_url=self.bot.user.display_avatar.url))
	
	@dono_main.subcommand(name="remove")
	async def dono_remove(
		self, 
		interaction: Interaction, 
		purpose: str = SlashOption(
			description="The purpose of the dono to remove the amoutn from",
			required=True,
			choices={
				"giveaways": "giveaway",
				"special": "special",
				"events": "event",
				"heists": "heist"
			}
		),
		user: Member = SlashOption(
			description="The user to remove the amount from",
			required=True
		), 
		amount: str = SlashOption(
			description="The amount to remove",
			required=True
		),
		reason: str = SlashOption(
			description="The reason for removal of this donation",
			required=True
		),
		note: str = SlashOption(
			description="An optional note to take regarding this donoation",
			required=False
		)
	):
		if interaction.user.id not in self.bot.DonoConfig.get("managers"):
			return await interaction.send("You are not authorized to do that!", ephemeral=True)

		amount = amount.replace(",", "")
		try:
			amount = convert_amount(amount)
		except:
			return await interaction.send("Invalid amount!", ephemeral=True)

		if amount < 1:
			return await interaction.send("Amount must be more than `1`", ephemeral=True)

		dono_before = await self.bot.dono_db.get_dono(user.id, purpose)
		await self.bot.dono_db.remove(user.id, purpose, amount)

		auto_roles = await self.bot.auto_dono_roles(user, dono_before-amount)

		await interaction.send(embed=Embed(
			title="Donation Removed",
			description=f"{user.mention}'s donation of **⏣ {amount:3,}** has been removed successfully!\nTotal donations for {purpose}: **⏣ {(dono_before - amount):3,}**\n{'The dono roles have been updated automatically!' if auto_roles else ''}",
			color=Colour.red()
			).set_thumbnail(url=interaction.guild.icon.url).set_footer(text="DB Bot | Donations", icon_url=self.bot.user.display_avatar.url))
		
		dono_log_channel = await self.bot.getch_channel(self.bot.DonoConfig.get("dono_log_channel"))
		if not dono_log_channel:
			return
		await dono_log_channel.send(embed=Embed(
			title="Donation Removed",
			description=f"""
Action by: {interaction.user.mention}
User: {user.mention}
Amount Removed: **⏣ {amount}**
Bank: {purpose}
Reason: {reason}
Note: {note}
""",
			color=Colour.red()
		).set_thumbnail(url=interaction.guild.icon.url).set_footer(text="DB Bot | Donations", icon_url=self.bot.user.display_avatar.url))

	@dono_main.subcommand(name="check")
	async def dono_check(
		self, 
		interaction: Interaction,
		user: Optional[Member] = SlashOption(
			description="The user to check the amount of",
			required=False
		), 
		purpose: str = SlashOption(
			description="The purpose of the dono to check",
			required=False,
			choices={
				"giveaways": "giveaway",
				"special": "special",
				"events": "event",
				"heists": "heist"
			}
		)
	):

		user = user or interaction.user
		title = "Your Donations" if user is interaction.user else f"{user.mention}'s Donations"

		if purpose is not None:
			amount = await self.bot.dono_db.get_dono(user.id, purpose.lower())
			description=f"Thank you for your donations! You've donated **⏣ {amount:3,}** for {purpose.title()} so far!" if amount != 0 else "You have no donations yet!",
		else:
			amount = await self.bot.dono_db.get_all(user.id)
			description=f"Thank you for your donations! You've donated a total of **⏣ {amount:3,}** so far!" if amount != 0 else "You have no donations yet!",
		
		embed = Embed(
			title=title,
			description=description[0],
			colour=Colour.green() if amount != 0 else Colour.red(),
		).set_thumbnail(url=interaction.guild.icon.url).set_footer(text="DB Bot | Donations", icon_url=self.bot.user.display_avatar.url)

		await interaction.send(embed=embed, ephemeral=True)



def setup(bot):
	bot.add_cog(DonoLogging(bot))
