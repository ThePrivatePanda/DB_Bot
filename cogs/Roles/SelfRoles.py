"""Configurations Used:
RolesConfig - 
	colour_roles: list[int]
	premium_colour_roles: list[int]
	ping_roles: list[int]
	personal_roles: list[int]
	player_type_roles: list[int]
	gender_roles: list[int]
	age_roles: list[int]
	residence_roles: list[int]

Config-
	self_roles_channel: int
"""
from discord import InteractionResponded
import nextcord
from nextcord import Interaction, Role, SelectOption

from nextcord.ext import commands
from nextcord.ext.commands import Bot
from datetime import date

class Confirm(nextcord.ui.View):
	def __init__(self):
		super().__init__()
		self.value = None

	@nextcord.ui.button(label='Confirm', style=nextcord.ButtonStyle.green)
	async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
		self.value = True
		self.stop()

	@nextcord.ui.button(label='Cancel', style=nextcord.ButtonStyle.grey)
	async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
		self.value = False
		self.stop()


class ColourDropdown(nextcord.ui.Select):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.my_roles_: list[Role] = [self.bot.guild.get_role(i) for i in self.bot.RolesConfig.get("colour_roles")]
		self.my_options_: list[SelectOption] = [
			SelectOption(label=i.name, value=i.id)
			for i in self.my_roles_
		]

		super().__init__(
			placeholder='Select your colour role!', 
			min_values=0, 
			max_values=1, 
			options=self.my_options_, 
			custom_id="colour_roles"
		)

	async def callback(self, interaction: Interaction) -> None:
		await interaction.response.defer(ephemeral=True, with_message=True)
		await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in [j for j in self.bot.RolesConfig.get("colour_roles")]+[k for k in self.bot.RolesConfig.get("premium_colour_roles")]])

		if len(self.values) == 0:
			return await interaction.followup.send("Removed all your colour roles.", ephemeral=True)

		new: Role = [i for i in self.my_roles_ if str(i.id) == self.values[0]][0]
		await interaction.user.add_roles(new)
		await interaction.followup.send(f"You now have the {new.mention} role.", ephemeral=True)

class PremiumDropdown(nextcord.ui.Select):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.my_roles_: list[Role] = [self.bot.guild.get_role(i) for i in self.bot.RolesConfig.get("premium_colour_roles")]
		self.my_options_: list[SelectOption] = [
			SelectOption(label=i.name, value=i.id)
			for i in self.my_roles_
		]
		super().__init__(placeholder='Select your premium colour role!', min_values=0, max_values=1, options=self.my_options_, custom_id="premium_roles")

	async def callback(self, interaction: Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in [j for j in self.bot.RolesConfig.get("colour_roles")]+[k for k in self.bot.RolesConfig.get("premium_colour_roles")]])
		
		if len(self.values) == 0:
			return await interaction.followup.send("Removed all your colour roles.", ephemeral=True)

		new: Role = [i for i in self.my_roles_ if str(i.id) == self.values[0]][0]
		await interaction.user.add_roles(new)
		await interaction.followup.send(f"You now have the {new.mention} role.", ephemeral=True)

class PingDropdown(nextcord.ui.Select):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.my_roles_: list[Role] = [self.bot.guild.get_role(i) for i in self.bot.RolesConfig.get("ping_roles")]
		self.my_options_: list[SelectOption] = [
			nextcord.SelectOption(label=i.name, value=i.id)
			for i in self.my_roles_
		]
		super().__init__(
			placeholder='Select your ping roles!', 
			min_values=0,
			max_values=len(bot.RolesConfig.get("ping_roles")),
			options=self.my_options_, 
			custom_id="ping_roles"
		)

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)

		if len(self.values) == 0:
			await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in self.bot.RolesConfig.get("ping_roles")])
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		old_roles = interaction.user.roles
		chosen: list[Role] = [i for i in self.my_roles_ if str(i.id) in self.values]

		rem: list[Role] = []
		add: list[Role] = []

		for i in chosen:
			if i in old_roles:
				rem.append(i)
				old_roles.pop(old_roles.index(i))
			else:
				add.append(i)
				old_roles.append(i)

		changes = "\n".join([f":green_circle: Added {i.name}" for i in add] + [f":red_circle: Removed {i.name}" for i in rem])

		embed = nextcord.Embed(title="Confirmation", description=f"The following changes will be done:\n{changes}").set_thumbnail(url=interaction.guild.icon.url)
		confirm_view = Confirm()

		mg = await interaction.send(embed=embed, view=confirm_view, ephemeral=True)
		await confirm_view.wait()

		for _item in confirm_view.children:
			_item.disabled = True

		if confirm_view.value is not True:
			await interaction.send('Well, ok, not then.', ephemeral=True)
			return

		await interaction.user.edit(roles=old_roles)
		now = ", ".join([i.mention for i in self.my_roles_ if i in interaction.user.roles])

		return await mg.edit(f"You now have the following roles:\n{now}.", embed=None, view=None)


class PlayerTypeDropdown(nextcord.ui.Select):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.my_roles_: list[Role] = [self.bot.guild.get_role(i) for i in self.bot.RolesConfig.get("player_type_roles")]
		self.my_options_: list[SelectOption]= [
			SelectOption(label=i.name, value=i.id)
			for i in self.my_roles_
		]
		super().__init__(
			placeholder='Select what kind of a dank player you are!',
			min_values=0,
            max_values=1, 
			options=self.my_options_,
			custom_id="player_type_roles"
		)

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		await interaction.user.remove_roles(*[i for i in self.my_roles_ if i in interaction.user.roles])

		if len(self.values) == 0:
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		new = [i for i in self.my_roles_ if str(i.id) == self.values[0]][0]

		await interaction.user.add_roles(new)
		await interaction.followup.send(f"You are now a {new.mention}.")


class PersonalDropdown(nextcord.ui.Select):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.my_roles_: list[Role] = [self.bot.guild.get_role(i) for i in self.bot.RolesConfig.get("personal_roles")]
		self.my_options_: list[SelectOption] = [
			SelectOption(label=i.name, value=i.id)
			for i in self.my_roles_
		]
		super().__init__(
			placeholder='Select some personal roles!',
			min_values=0,
			max_values=1,
			options=self.my_options_,
			custom_id="personal_roles"
		)

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)

		possibles_gender = self.bot.RolesConfig.get("gender_roles")
		possibles_age = self.bot.RolesConfig.get("age_roles")

		if len([i for i in possibles_gender if str(i) in self.values]) == 2 or len([i for i in possibles_age if str(i) in self.values]) == 2:
			return await interaction.followup.send("You can have only a single role of this kind. Please restart.")

		if len(self.values) == 1:
			id = int(self.values[0])
			if id in possibles_gender:
				await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in possibles_gender])
			elif id in possibles_age:
				await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in possibles_age])
			await interaction.user.add_roles([i for i in self.my_roles_ if i.id == id][0])
			return await interaction.followup.send("Al' done.")

		await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in self.bot.RolesConfig.get("personal_roles")])
		if len(self.values) == 0:
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		if len(self.values) == 2:
			await interaction.user.add_roles(*[i for i in self.my_roles_ if str(i.id) in self.values])

		await interaction.followup.send("Al' done.")


class ResidenceDropdown(nextcord.ui.Select):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.my_roles_: list[Role] = [self.bot.guild.get_role(i) for i in self.bot.RolesConfig.get("residence_roles")]
		self.my_options_: list[SelectOption] = [
			SelectOption(label=i.name, value=i.id)
			for i in self.my_roles_
		]
		super().__init__(
			placeholder='Select where you live!',
			min_values=0,
            max_values=1,
			options=self.my_options_,
			custom_id="residence_roles"
		)

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in self.bot.RolesConfig.get("residence_roles")])

		if len(self.values) == 0:
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		new = [i for i in self.my_roles_ if str(i.id) == self.values[0]][0]
		await interaction.user.add_roles(new)
		await interaction.followup.send(f"You now have the {new.mention} role.")



class ColourDropdownView(nextcord.ui.View):
	def __init__(self, bot: Bot):
		super().__init__(timeout=None)
		self.add_item(ColourDropdown(bot))

class PremiumDropdownView(nextcord.ui.View):
	def __init__(self, bot):
		super().__init__(timeout=None)
		self.add_item(PremiumDropdown(bot))

class PingDropdownView(nextcord.ui.View):
	def __init__(self, bot: Bot):
		super().__init__(timeout=None)
		self.add_item(PingDropdown(bot))

class PlayerTypeDropdownView(nextcord.ui.View):
	def __init__(self, bot: Bot):
		super().__init__(timeout=None)
		self.add_item(PlayerTypeDropdown(bot))

class PersonalDropdownView(nextcord.ui.View):
	def __init__(self, bot: Bot):
		super().__init__(timeout=None)
		self.add_item(PersonalDropdown(bot))

class ResidenceDropdownView(nextcord.ui.View):
	def __init__(self, bot: Bot):
		super().__init__(timeout=None)
		self.add_item(ResidenceDropdown(bot))


class SelfRoles(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.bot.loop.create_task(self.create_views())

	async def create_views(self):
		await self.bot.wait_until_ready()
		if not self.bot.selfrole_view_set:
			self.bot.add_view(ColourDropdownView(self.bot))
			self.bot.add_view(PremiumDropdownView(self.bot))
			self.bot.add_view(PingDropdownView(self.bot))
			self.bot.add_view(PlayerTypeDropdownView(self.bot))
			self.bot.add_view(PersonalDropdownView(self.bot))
			self.bot.add_view(ResidenceDropdownView(self.bot))
			self.bot.selfrole_view_set = True

	@commands.group("selfrole")
	async def selfrole(self, ctx):
		pass

	@selfrole.command()
	@commands.is_owner()
	async def colour(self, ctx: commands.Context, here=False):
		"""Sends a message with our dropdown containing colour roles view"""
		view = ColourDropdownView(self.bot)
		delim = '\n'.join([ctx.guild.get_role(i).mention for i in self.bot.RolesConfig.get("colour_roles")])
		embed = nextcord.Embed(
			title="Colour Role", 
			description=f"Select a role to make your name appear colourful in chat!\n{delim}",
			colour=0xfffa65).set_thumbnail(
				url=ctx.guild.icon.url
			).set_footer(
				icon_url=ctx.guild.me.display_avatar.url,
				text=f"DB Bot | Selfroles"
			)
		
		if here is not False:
			await self.bot.get_channel(self.bot.RolesConfig.get("self_roles_channel")).send(embed=embed, view=view)
		else:
			await ctx.send(embed=embed, view=view)

	@selfrole.command()
	@commands.is_owner()
	async def premium(self, ctx: commands.Context, here=False):
		"""Sends a message with our dropdown containing premium colour roles view"""
		view = PremiumDropdownView(self.bot)
		delim = '\n'.join([ctx.guild.get_role(
			i).mention for i in self.bot.RolesConfig.get("premium_colour_roles")])
		embed = nextcord.Embed(
                    title="Premium Colour Role",
                    description=f"Select a role to make your name appear colourful in chat!\n{delim}",
                    colour=0xfffa65).set_thumbnail(
                    url=ctx.guild.icon.url
                ).set_footer(
                    icon_url=ctx.guild.me.display_avatar.url,
                    text=f"DB Bot | Selfroles"
                )

		if here is not False:
			await self.bot.get_channel(self.bot.RolesConfig.get("premium_roles_channel")).send(embed=embed, view=view)
		else:
			await ctx.send(embed=embed, view=view)

	@selfrole.command()
	@commands.is_owner()
	async def ping(self, ctx: commands.Context, here=False):
		"""Sends a message with our dropdown containing ping roles view"""
		view = PingDropdownView(self.bot)
		delim = '\n'.join([ctx.guild.get_role(
			i).mention for i in self.bot.RolesConfig.get("ping_roles")])
		embed = nextcord.Embed(
                    title="Ping Roles",
                    description=f"Take some roles to get notified about certain events taking place!\n{delim}",
                    colour=0xfffa65).set_thumbnail(
                    url=ctx.guild.icon.url
                ).set_footer(
                    icon_url=ctx.guild.me.display_avatar.url,
                    text=f"DB Bot | Selfroles"
                )

		if here is not False:
			await self.bot.get_channel(self.bot.RolesConfig.get("self_roles_channel")).send(embed=embed, view=view)
		else:
			await ctx.send(embed=embed, view=view)


	@selfrole.command(aliases=["pt", "playertype"])
	@commands.is_owner()
	async def player(self, ctx: commands.Context, here=False):
		"""Sends a message with our dropdown containing player type roles view"""
		view = PlayerTypeDropdownView(self.bot)
		delim = '\n'.join([ctx.guild.get_role(
			i).mention for i in self.bot.RolesConfig.get("player_type_roles")])
		embed = nextcord.Embed(
                    title="Player Type role",
                    description=f"Let people know what kind of a dank player you are!\n{delim}",
                    colour=0xfffa65).set_thumbnail(
                    url=ctx.guild.icon.url
                ).set_footer(
                    icon_url=ctx.guild.me.display_avatar.url,
                    text=f"DB Bot | Selfroles"
                )

		if here is not False:
			await self.bot.get_channel(self.bot.RolesConfig.get("self_roles_channel")).send(embed=embed, view=view)
		else:
			await ctx.send(embed=embed, view=view)

	@selfrole.command()
	@commands.is_owner()
	async def personal(self, ctx: commands.Context, here=False):
		"""Sends a message with our dropdown containing personal roles view"""
		view = PersonalDropdownView(self.bot)
		delim = '\n'.join([ctx.guild.get_role(
			i).mention for i in self.bot.RolesConfig.get("personal_roles")])
		embed = nextcord.Embed(
                    title="Player Type role",
                    description=f"Let people about yourself!\n{delim}",
                    colour=0xfffa65).set_thumbnail(
                    url=ctx.guild.icon.url
                ).set_footer(
                    icon_url=ctx.guild.me.display_avatar.url,
                    text=f"DB Bot | Selfroles"
                )

		if here is not False:
			await self.bot.get_channel(self.bot.RolesConfig.get("self_roles_channel")).send(embed=embed, view=view)
		else:
			await ctx.send(embed=embed, view=view)

	@selfrole.command()
	@commands.is_owner()
	async def residence(self, ctx: commands.Context, here=False):
		"""Sends a message with our dropdown containing personal  roles view"""
		view = ResidenceDropdownView(self.bot)
		delim = '\n'.join([ctx.guild.get_role(
			i).mention for i in self.bot.RolesConfig.get("residence_roles")])
		embed = nextcord.Embed(
                    title="Continent of residence role",
                    description=f"Let people know where you are from!\n{delim}",
                    colour=0xfffa65).set_thumbnail(
                    url=ctx.guild.icon.url
                ).set_footer(
                    icon_url=ctx.guild.me.display_avatar.url,
                    text=f"DB Bot | Selfroles"
                )

		if here is not False:
			await self.bot.get_channel(self.bot.RolesConfig.get("self_roles_channel")).send(embed=embed, view=view)
		else:
			await ctx.send(embed=embed, view=view)


def setup(bot):
	bot.add_cog(SelfRoles(bot))