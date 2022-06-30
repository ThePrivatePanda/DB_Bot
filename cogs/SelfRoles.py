import nextcord

from nextcord.ext import commands
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
	def __init__(self):
		self.my_options_ = [
			nextcord.SelectOption(label='Red', description='Make your name appear red in chat!', value='819088603849293914'),
			nextcord.SelectOption(label='Orange', description='Make your name appear orange in chat!', value='819088605753901056'),
			nextcord.SelectOption(label='Yellow', description='Make your name appear yellow in chat!', value='819088607326765068'),
			nextcord.SelectOption(label='Green', description='Make your name appear green in chat!', value='819088609369260063'),
			nextcord.SelectOption(label='Blue', description='Make your name appear blue in chat!', value='819088611990962196'),
			nextcord.SelectOption(label='Purple', description='Make your name appear purple in chat!', value='819088614159548496'),
			nextcord.SelectOption(label='Pink', description='Make your name appear pink in chat!', value='819090264589074442'),
		]

		super().__init__(placeholder='Select your colour role!', min_values=0, max_values=1, options=self.my_options_, custom_id="colour_roles")

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		if len(self.values) == 0:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in [int(j.value) for j in self.my_options_]])
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)
		user_roles = [i.id for i in interaction.user.roles]
		possibles = [int(i.value) for i in self.my_options_]

		if len([i for i in possibles if i in user_roles]) > 1:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in possibles])
		new = interaction.guild.get_role(int(self.values[0]))
		await interaction.user.add_roles(new)

		await interaction.followup.send(f"You now have the {new.name} role.")

class PremiumDropdown(nextcord.ui.Select):
	def __init__(self):
		self.my_options_ = [
			nextcord.SelectOption(label='Red', description='Make your name appear red in chat!', value='819088603849293914'),
			nextcord.SelectOption(label='Orange', description='Make your name appear orange in chat!', value='819088605753901056'),
			nextcord.SelectOption(label='Yellow', description='Make your name appear yellow in chat!', value='819088607326765068'),
			nextcord.SelectOption(label='Green', description='Make your name appear green in chat!', value='819088609369260063'),
			nextcord.SelectOption(label='Blue', description='Make your name appear blue in chat!', value='819088611990962196'),
			nextcord.SelectOption(label='Purple', description='Make your name appear purple in chat!', value='819088614159548496'),
			nextcord.SelectOption(label='Pink', description='Make your name appear pink in chat!', value='819090264589074442'),
		]

		super().__init__(placeholder='Select your colour role!', min_values=0, max_values=1, options=self.my_options_, custom_id="premium_roles")

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		if len(self.values) == 0:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in [int(j.value) for j in self.my_options_]])
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)
		user_roles = [i.id for i in interaction.user.roles]
		possibles = [int(i.value) for i in self.my_options_]

		if len([i for i in possibles if i in user_roles]) > 1:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in possibles])
		new = interaction.guild.get_role(int(self.values[0]))
		await interaction.user.add_roles(new)

		await interaction.followup.send(f"You now have the {new.name} role.")

class PingDropdown(nextcord.ui.Select):
	def __init__(self):
		self.my_options_ = [
			nextcord.SelectOption(label='Announcement ping', description='Get pinged on an announcement!', value='819090772014923787'),
			nextcord.SelectOption(label='Large Giveaway ping', description='Get pinged when a large dank giveaway happens!', value='819090776734040066'),
			nextcord.SelectOption(label='Small Giveaway Ping', description='Get notified when a small giveaway takes place!', value='819090779460206592'),
			nextcord.SelectOption(label='General Events ping', description='Get pinged when an in-server event is gonna happen!', value="819090780525428736"),
			nextcord.SelectOption(label='Large Heist Ping', description='Get notified when a large heist[100m] happens!', value="819651753850568724"),
			nextcord.SelectOption(label='Other Heist Ping', description='other heist may happen :eyes:', value="821515809745535026"),
		]

		super().__init__(placeholder='Select ping roles!', min_values=0, max_values=6, options=self.my_options_, custom_id="ping_roles")

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		if len(self.values) == 0:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in [int(j.value) for j in self.my_options_]])
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		changes = []
		rem, add = [], []
		chosen = [interaction.guild.get_role(int(i)) for i in self.values]
		before = [int(i.value) for i in self.my_options_ if i in interaction.user.roles]

		for i in chosen:
			if i in interaction.user.roles:
				changes.append(f":red_circle: {i.name} will be removed")
				rem.append(i)
			else:
				changes.append(f":green_circle: {i.name} will be added")
				add.append(i)
		pain = '\n'.join(changes)
		embed = nextcord.Embed(title="Confirmation", description=f"The following changes will be done:\n {pain}").set_thumbnail(url=interaction.guild.icon.url)

		confirm_view = Confirm()
		mg = await interaction.send(embed=embed, view=confirm_view, ephemeral=True)
		await confirm_view.wait()
		for _item in confirm_view.children:
			_item.disabled = True

		if confirm_view.value is not True:
			await interaction.send('Well, not then.', ephemeral=True)
			return
		
		now = [i for i in before if i not in [j.id for j in rem]]
		for i in [i.id for i in add]:
			now.append(i)
		now = [interaction.guild.get_role(i) for i in now]

		await interaction.user.remove_roles(*rem)
		await interaction.user.add_roles(*add)
		await mg.edit(f"You now have the following roles:\n {', '.join([i.name for i in now])}", embed=None, view=None)
		return

class PlayerTypeDropdown(nextcord.ui.Select):
	def __init__(self):
		self.my_options_ = [
			nextcord.SelectOption(label='Trader', value='990308025480925224'),
			nextcord.SelectOption(label='Collector', value='990308038311288902'),
			nextcord.SelectOption(label='Gambler', value='990307945340342342'),
			nextcord.SelectOption(label='Fighter', value='990308032741244950'),
		]

		super().__init__(placeholder='Select your Player Type role!', min_values=0, max_values=1, options=self.my_options_, custom_id="playertype_roles")

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		if len(self.values) == 0:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in [int(j.value) for j in self.my_options_]])
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		user_roles = [i.id for i in interaction.user.roles]
		possibles = [int(i.value) for i in self.my_options_]

		if len([i for i in possibles if i in user_roles]) > 1:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in possibles])
		new = interaction.guild.get_role(int(self.values[0]))
		await interaction.user.add_roles(new)

		await interaction.followup.send(f"You are now a {new.name}.")


class PersonalDropdown(nextcord.ui.Select):
	def __init__(self):
		self.my_options_ = [
			nextcord.SelectOption(label='He/Him', value='819101340269281321'),
			nextcord.SelectOption(label='She/her', value='819101299869483010'),
			nextcord.SelectOption(label='They/Them', value='842199505239670815'),
			nextcord.SelectOption(label='18+', value='819101716149436436'),
			nextcord.SelectOption(label='<18', value='819101765604474890'),
		]

		super().__init__(placeholder='Select your personal roles!', min_values=0, max_values=2, options=self.my_options_, custom_id="personal_roles")

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		if len(self.values) == 0:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in [int(j.value) for j in self.my_options_]])
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		possibles_gender = [819101340269281321, 819101299869483010, 842199505239670815]
		possibles_age = [819101716149436436, 819101765604474890]

		if len([i for i in possibles_gender if i in [int(j) for j in self.values]]) == 2 or len([i for i in possibles_age if i in [int(j) for j in self.values]]) == 2:
			await interaction.followup.send("You can have only a single role of this kind. Please restart.")
		if len(self.values) == 2:
			await interaction.user.remove_roles(*[interaction.guild.get_role(int(i.value)) for i in self.my_options_])
			await interaction.user.add_roles(*[interaction.guild.get_role(int(i)) for i in self.values])
		if len(self.values) == 1:
			id = int(self.value[0])
			if id in possibles_gender:
				await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in possibles_gender])
			elif id in possibles_age:
				await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in possibles_age])
			await interaction.user.add_roles(*[interaction.guild.get_role(id)])

		await interaction.followup.send("Al' dun.")

class CORDropdown(nextcord.ui.Select):
	def __init__(self):
		self.my_options_ = [
			nextcord.SelectOption(label='Africa', value='819104954308493322'),
			nextcord.SelectOption(label='Asia', value='819104731963457536'),
			nextcord.SelectOption(label='Australia', value='819109907248840704'),
			nextcord.SelectOption(label='Europe', value='819162497276837910'),
			nextcord.SelectOption(label='North America', value='819104786635816980'),
			nextcord.SelectOption(label='South America', value='819108007107493928'),
		]

		super().__init__(placeholder='Select your continent of residence!', min_values=0, max_values=1, options=self.my_options_, custom_id="cor_roles")

	async def callback(self, interaction: nextcord.Interaction):
		await interaction.response.defer(ephemeral=True, with_message=True)
		if len(self.values) == 0:
			await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in [int(j.value) for j in self.my_options_]])
			return await interaction.followup.send("Removed all your roles from this dropdown", ephemeral=True)

		possibles = [int(i.value) for i in self.my_options_]

		await interaction.user.remove_roles(*[interaction.guild.get_role(i) for i in possibles])
	  
		new = interaction.guild.get_role(int(self.values[0]))
		await interaction.user.add_roles(interaction.guild.get_role(int(self.values[0])))

		await interaction.followup.send(f"You now have the {new.name} role.")


class ColourDropdownView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(ColourDropdown())

class PremiumDropdownView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(PremiumDropdown())

class PingDropdownView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(PingDropdown())

class PlayerTypeDropdownView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(PlayerTypeDropdown())

class PersonalDropdownView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(PersonalDropdown())

class CORDropdownView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(CORDropdown())


class SelfRoles(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.bot.loop.create_task(self.create_views())
		self.bot.all_colours = [
			819088603849293914,
			819088605753901056,
			819088607326765068,
			819088609369260063,
			819088611990962196,
			819088614159548496,
			819090264589074442
		]

	async def create_views(self):
		if not self.bot.persistent_views_added:
			self.bot.add_view(ColourDropdownView())
			self.bot.add_view(PingDropdownView())
			self.bot.add_view(PlayerTypeDropdownView())
			self.bot.add_view(PersonalDropdownView())
			self.bot.add_view(CORDropdownView())
			self.bot.persistent_views_added = True

	async def sendsendsend(self, here, ctx, embed, view):
		if here:
			channel = ctx.channel
		else:
			channel = await self.bot.getch_channel(self.bot.config.get("self_roles_channel"))
		await channel.send(embed=embed, view=view)

  
	@commands.group("selfrole")
	async def selfrole(self, ctx):
		pass

	@selfrole.command()
	@commands.is_owner()
	async def colour(self, ctx, here=False):
		"""Sends a message with our dropdown containing colour roles view"""
		view = ColourDropdownView()
		embed = nextcord.Embed(title="Colour Role", description="""
Select a role to make your name appear colourful in chat!
<@&819088603849293914>
<@&819088605753901056>
<@&819088607326765068>
<@&819088609369260063>
<@&819088611990962196>
<@&819088614159548496>
<@&819090264589074442>
""", colour=0xfffa65).set_thumbnail(url=ctx.guild.icon.url).set_footer(icon_url=ctx.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		await self.sendsendsend(here, ctx, embed, view)

	@selfrole.command()
	@commands.is_owner()
	async def premium(self, ctx, here=False):
		"""Sends a message with our dropdown containing premium colour roles view"""
		view = ColourDropdownView()
		embed = nextcord.Embed(title="Colour Role", description="""
Select a role to make your name appear colourful in chat!
<@&819088603849293914>
<@&819088605753901056>
<@&819088607326765068>
<@&819088609369260063>
<@&819088611990962196>
<@&819088614159548496>
<@&819090264589074442>
""", colour=0xfffa65).set_thumbnail(url=ctx.guild.icon.url).set_footer(icon_url=ctx.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		await self.sendsendsend(here, ctx, embed, view)

	@selfrole.command()
	@commands.is_owner()
	async def ping(self, ctx, here=False):
		"""Sends a message with our dropdown containing ping roles view"""
		view = PingDropdownView()
		embed = nextcord.Embed(title="Ping Roles", description="""
Select some roles to get notified for various things!
📢<@&819090772014923787>
💝<@&819090776734040066>
🎉<@&819090779460206592>
🎲<@&819090780525428736>
🏦<@&819651753850568724>
💸<@&821515809745535026>
""", colour=0xfffa65).set_thumbnail(url=ctx.guild.icon.url).set_footer(icon_url=ctx.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		await self.sendsendsend(here, ctx, embed, view)


	@selfrole.command(aliases=["pt", "playertype"])
	@commands.is_owner()
	async def player(self, ctx, here=False):
		"""Sends a message with our dropdown containing player type roles view"""
		view = PlayerTypeDropdownView()
		embed = nextcord.Embed(title="Type of Dank Player Roles", description="""
Select a role to let people know what kind of a dank player you are!
<@&990308025480925224>
<@&990308038311288902>
<@&990307945340342342>
<@&990308032741244950>
""", colour=0xfffa65).set_thumbnail(url=ctx.guild.icon.url).set_footer(icon_url=ctx.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		await self.sendsendsend(here, ctx, embed, view)

	@selfrole.command()
	@commands.is_owner()
	async def personal(self, ctx, here=False):
		"""Sends a message with our dropdown containing personal  roles view"""
		view = PersonalDropdownView()
		embed = nextcord.Embed(title="Personal Roles", description="""
Select some roles about yourself!
<@&819101340269281321>
<@&842199505239670815>
<@&819101299869483010>
<@&819101716149436436>
<@&819101765604474890>
""", colour=0xfffa65).set_thumbnail(url=ctx.guild.icon.url).set_footer(icon_url=ctx.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		await self.sendsendsend(here, ctx, embed, view)

	@selfrole.command()
	@commands.is_owner()
	async def residence(self, ctx, here=False):
		"""Sends a message with our dropdown containing personal  roles view"""
		view = CORDropdownView()
		embed = nextcord.Embed(title="Country of Residence Role", description="""
Select a role to show your country of residence!
<@&819104954308493322>
<@&819104731963457536>
<@&819109907248840704>
<@&819162497276837910>
<@&819104786635816980>
<@&819108007107493928>
""", colour=0xfffa65).set_thumbnail(url=ctx.guild.icon.url).set_footer(icon_url=ctx.guild.me.display_avatar.url, text=f"DB Bot | {date.today().strftime('%B %d, %Y')}")
		await self.sendsendsend(here, ctx, embed, view)


def setup(bot):
	bot.add_cog(SelfRoles(bot))