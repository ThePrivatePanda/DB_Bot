from nextcord import Interaction, Member, Object, SelectOption, slash_command, SlashOption
from nextcord.ext.commands import Cog
from nextcord.ui import Select, View
from nextcord.utils import get


class RolesView(View):
    def __init__(self, *, member: Member, role_type_choice):
        super().__init__(timeout=None)

        self.add_item(RolesSelect(member=member, role_type_choice=role_type_choice))


class RolesSelect(Select["RolesView"]):
    def __init__(self, *, member: Member, role_type_choice):
        self.role_type_choice = role_type_choice
        self.limits_dict = {
            "ping": 7,
            "personal": 5,
            "colour": 1,
            "partnership": 1,
            "typeofplayer": 1
        }
        self.choices_dict = {
            "ping": [
                819090772014923787,
                819090776734040066,
                819090779460206592,
                819090780525428736,
                819651753850568724,
                819706474774921256,
                821515809745535026,
            ],
            "personal": [
                819101340269281321,
                819101299869483010,
                842199505239670815,
                819101716149436436,
                819101765604474890,
            ],
            "colour": [
                819088603849293914,
                819088605753901056,
                819088607326765068,
                819088609369260063,
                819088611990962196,
                819088614159548496,
                819090264589074442,
            ],
            "partnership": [
                820788214717218816,
                820792593972854835,
            ],
            "typeofplayer": [
                990308025480925224,
                990308038311288902,
                990307945340342342,
                990308032741244950,
            ],
        }
        self.choices = self.choices_dict[role_type_choice]
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
        roles = interaction.user.roles  # type: ignore

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
        user_roles = [j.id for j in roles]
        if self.role_type_choice == "personal":
              if len([i for i in [819101340269281321, 819101299869483010, 842199505239670815] if i in user_roles]) > 1:
                  return await interaction.edit(content="You can have only a single role of this kind.", view=self.view)
              if len([i for i in [819101716149436436, 819101765604474890] if i in user_roles]) > 1:
                  return await interaction.edit(content="You can have only a single role of this kind.", view=self.view)
                
        await interaction.user.edit(roles=roles)

        new_roles = [
            interaction.guild.get_role(int(value)).name  # type: ignore
            for value in self.values
        ]

        await interaction.edit(
            content=f"You now have {', '.join(new_roles) or 'no roles'}", view=self.view
        )


class Roles(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="roles", guild_ids=[819084505037799465], description="Self assign roles")
    async def slashroles(self,
        interaction: Interaction,
        role_type = SlashOption(
            description="What type of roles do you want to select from?",
            required=True,
            choices={
                "Ping Roles": "ping",
                "Personal Roles": "personal",
                "Colour Role": "colour",
                "Partnership Roles": "partnership",
                "Type of dank Player": "typeofplayer"
            },
        )
    ):  
        await interaction.send(
            "Select your new roles",
            view=RolesView(member=interaction.user, role_type_choice=role_type),
            ephemeral=True,
        )


def setup(bot):
    bot.add_cog(Roles(bot))
