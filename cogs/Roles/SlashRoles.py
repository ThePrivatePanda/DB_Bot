"""Configurations Used:
RolesConfig -
	colour_roles: list[int]
	premium_colour_roles: list[int]
	ping_roles: list[int]
	personal_roles: list[int]
	player_type_roles: list[int]
	residence_roles: list[int]

	premium_colours_allowed_roles  list[int] - The roles that can take premium colours.
	premium_colours_allowed_users  list[int] - Particular users that can take premium colours.
"""

from code import interact
from discord import Role
from nextcord import Interaction, Member, Object, SelectOption, slash_command, SlashOption
from nextcord.ext.commands import Cog
from nextcord.ui import Select, View
from nextcord.utils import get
from nextcord.ext.commands import Bot
from ConfigHandler import Config

class RolesView(View):
	def __init__(self, *, member: Member, role_type_choice, bot):
		super().__init__(timeout=None)
		self.add_item(RolesSelect(member=member, role_type_choice=role_type_choice, bot=bot))


class RolesSelect(Select["RolesView"]):
	def __init__(self, *, member: Member, role_type_choice, bot: Bot):
		self.bot = bot
		self.role_type_choice = role_type_choice
		self.limits_dict = {
			"colour_roles": 1,
			"premium_colour_roles": 1,
			"ping_roles": len(self.bot.RolesConfig.get("ping_roles")),
			"personal_roles": 5,
			"player_type_roles": 1,
			"residence_roles": 1
		}
		self.choices_ = self.bot.RolesConfig.get(role_type_choice)
		self.roles_: list[Role] = [member.guild.get_role(i) for i in self.choices_]
		super().__init__(
			placeholder="Select your new roles",
			min_values=0,
			max_values=self.limits_dict[role_type_choice],
			options=[
				SelectOption(
					label=i.name,  # type: ignore
					value=str(i.id),
					default=member.get_role(i.id) is not None,
				)
				for i in self.roles_
			],
		)

	async def callback(self, interaction: Interaction):
		roles = interaction.user.roles  # type: ignore

		if self.role_type_choice in ("colour_roles", "premium_colour_roles"):
			await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in [j for j in self.bot.RolesConfig.get("colour_roles")]+[k for k in self.bot.RolesConfig.get("premium_colour_roles")]])

			if self.role_type_choice == "premium_roles":
				allowed_roles = [i for i in self.bot.config.get("premium_colours_allowed_roles")]
				allowed_users = [i for i in self.bot.config.get("premium_colours_allowed_users")]
				if len([i for i in allowed_roles if i in interaction.user.roles]) > 0 or interaction.user.id in allowed_users:
					pass
				else:
					return await interaction.followup.send("You are not allowed to take premium colours!", ephemeral=True)

			await interaction.user.add_roles(*[i for i in self.roles_ if str(i.id) in self.values])

		if self.role_type_choice == "personal_roles":
			if len([i for i in self.bot.RolesConfig.get("gender_roles") if i in self.values]) > 1:
				return await interaction.followup.send(content="You can have only a single role of this kind.", view=self.view, ephemeral=True)
			if len([i for i in self.bot.RolesConfig.get("age_roles") if i in self.values]) > 1:
				return await interaction.followup.edit(content="You can have only a single role of this kind.", view=self.view, ephemeral=True)
			else:
				await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in [j for j in self.bot.RolesConfig.get("personal_roles")]])
				await interaction.user.add_roles(*[i for i in self.roles_ if str(i.id) in self.values])

		elif self.role_type_choice in ("residence_roles", "player_type_roles"):
			await interaction.user.edit(roles=[i for i in interaction.user.roles if i.id not in [j for j in self.bot.RolesConfig.get("residence_roles")]+[k for k in self.bot.RolesConfig.get("player_type_roles")]])
			await interaction.user.add_roles([i for i in self.roles_ if i.id == int(self.values[0])][0])

		elif self.role_type_choice == "ping_roles":
			for role_id in self.values:
				role_id = int(role_id)
				if (
					interaction.user.get_role(role_id) is None
					and str(role_id) in self.values
				):
					# user does not have the role but wants it
					roles.append(Object(role_id))
					option = get(self.options, value=str(role_id))
					if option is not None:
						option.default = True
				elif (
					interaction.user.get_role(role_id) is not None
					and str(role_id) not in self.values
				):
					# user has the role but does not want it
					role_ids = [r.id for r in roles]
					roles.pop(role_ids.index(role_id))
					option = get(self.options, value=str(role_id))
					if option is not None:
						option.default = False

			await interaction.user.edit(roles=roles)

		new_roles = [i.mention for i in self.roles_ if str(i.id) in self.values]

		await interaction.edit(content=f"You now have {', '.join(new_roles) or 'no roles of this dropdown'}.", view=None)


class Roles(Cog):
	def __init__(self, bot):
		self.bot = bot

	@slash_command(name="selfrole", guild_ids=[819084505037799465], description="Self assign roles")
	async def slashroles(self,
		interaction: Interaction,
		role_type = SlashOption(
			description="What type of roles do you want to select from?",
			required=True,
			choices={
				"Colour Role": "colour_roles",
				"Premium Colour Role": "premium_colour_roles",
				"Ping Roles": "ping_roles",
				"Personal Roles": "personal_roles",
				"Type of dank Player": "player_type_roles",
				"Continent of residence": "residence_roles"
			},
		)
	):  
		await interaction.send(
			"Select your new roles",
			view=RolesView(member=interaction.user, role_type_choice=role_type, bot=self.bot),
			ephemeral=True,
		)


def setup(bot):
	bot.add_cog(Roles(bot))
