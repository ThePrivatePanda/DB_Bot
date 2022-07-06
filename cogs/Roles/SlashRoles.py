"""Configurations Used:
possible_colour_roles          list[int] - A list of role ids of all possible colour roles. These are used to atomically remove all colour roles when taking a new one
premium_colours_allowed_roles  list[int] - The roles that can take premium colours.
premium_colours_allowed_users  list[int] - Particular users that can take premium colours.
"""

from nextcord import Interaction, Member, Object, SelectOption, slash_command, SlashOption
from nextcord.ext.commands import Cog
from nextcord.ui import Select, View
from nextcord.utils import get
from nextcord.ext.commands import Bot

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
		self.choices = self.bot.RolesConfig.get(role_type_choice)
		super().__init__(
			placeholder="Select your new roles",
			min_values=0,
			max_values=self.limits_dict[role_type_choice],
			options=[
				SelectOption(
					label=member.guild.get_role(role_id).name,  # type: ignore
					value=str(role_id),
					default=member.get_role(role_id) is not None,
				)
				for role_id in self.choices
			],
		)

	async def callback(self, interaction: Interaction):
		await interaction.response.defer(with_message=True, ephemeral=True)

		roles = interaction.user.roles  # type: ignore
		user_roles = [j.id for j in roles]

		if self.role_type_choice == "personal_roles":
			if len([i for i in self.bot.RolesConfig.get("gender_roles") if i in user_roles]) > 1:
				return await interaction.followup.send(content="You can have only a single role of this kind.", view=self.view, ephemeral=True)
			if len([i for i in self.bot.RolesConfig.get("ge_roles") if i in user_roles]) > 1:
				return await interaction.followup.edit(content="You can have only a single role of this kind.", view=self.view, ephemeral=True)

		elif self.role_type_choice in ("COR", "player_type"):
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in self.choices_dict[self.role_type_choice]])
			await interaction.user.add_roles(interaction.guild.get_role(self.choices[0]))

		elif self.role_type_choice in ("colour", "premium"):
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in self.bot.config.get("possible_colour_roles")])
			await interaction.user.add_roles(interaction.guild.get_role(self.choices[0]))

		if self.role_type_choice == "premium":
			allowed_roles = [interaction.guild.get_role(i) for i in self.bot.config.get("premium_colours_allowed_roles")]
			if len([i for i in allowed_roles if i in interaction.user.roles]) > 0 or interaction.user.id in self.bot.config.get("premium_colours_allowed_users"):
				await interaction.user.add_roles(interaction.guild.get_role(self.choices[0]))
			else:
				return await interaction.followup.send("You are not allowed to take premium colours!", ephemeral=True)
		elif self.role_type_choice == "ping":
			for role_id in self.choices:
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

		new_roles = [
			interaction.guild.get_role(int(value)).name  # type: ignore
			for value in self.values
		]

		await interaction.edit_original_message(
			content=f"You now have {', '.join(new_roles) or 'no roles'}", view=self.view
		)


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
				"Your continent of residence": "residenc_rolese"
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
