from discord import Guild
from nextcord import Intents
from BotBase import BotBaseBot
from ConfigHandler import Config
from typing import List
import aiosqlite
import DatabaseHandlers


bot: BotBaseBot = BotBaseBot(command_prefix="db", case_insensitive=True, strip_after_prefix=True, intents=Intents.all())

cogs: List[str] = [
	"jishaku",

	"cogs.Configuration",
	"cogs.Counting",
	"cogs.Grinders",
	"cogs.Owner",
	"cogs.SelfRoles",
	"cogs.SlashRoles",
	"cogs.Support",
]

@bot.event
async def on_ready() -> None:
	print(f"Logged in as {bot.user}")

async def startup():
	print("starting up...")
	bot.selfrole_view_set = False
	bot.support_view_set = False
	bot.owner_id = 736147895039819797

	await bot.wait_until_ready()
	# bot vars
	bot.guild: Guild = await bot.getch_guild(964100538805407794)
	bot.owner = await bot.getch_user(bot.owner_id)
	print("Set bot variables")

	# db stuff
	bot.db = await aiosqlite.connect("dbs/db.sqlite3")
	bot.grinders_db: DatabaseHandlers.GrinderDatabaseHandler = DatabaseHandlers.GrinderDatabaseHandler(bot)
	bot.allowances_db: DatabaseHandlers.AllowancesDatabaseHandler = DatabaseHandlers.AllowancesDatabaseHandler(bot)
	print("Setup DB")

	# cogs
	for extension in cogs:
		try:
			bot.load_extension(extension)
			print(f"Successfully loaded extension {extension}")
		except Exception as e:
			exc = f"{type(e).__name__,}: {e}"
			print(f"Failed to load extension {extension}\n{exc}")

	await bot.resync_slash_commands()

	print("Synced slash commands")
	await bot.owner.send("All Ready")
	print("All Ready")

bot.config = Config("config.json")
bot.CountingConfig = Config("cogs/Counting/CountingConfig.json")
bot.RolesConfig = Config("cogs/Roles/RolesConfig.json")

bot.loop.create_task(startup())
bot.run(bot.config.get("token"))