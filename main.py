from nextcord import Intents
from BotBase import BotBaseBot
from ConfigHandler import Config
from typing import List
import aiosqlite
import DatabaseHandlers


bot: BotBaseBot = BotBaseBot(command_prefix="db", case_insensitive=True, strip_after_prefix=True, intents=Intents.all())

cogs: List[str] = [
    "jishaku",

    "cogs.Grinders",
    "cogs.Owner",
    "cogs.SelfRoles",
    "cogs.SlashRoles",
]

@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")

async def startup():
    print("starting up...")
    bot.persistent_views_added = False

    await bot.wait_until_ready()
    # bot vars
    bot.guild = await bot.getch_guild(964100538805407794)
    bot.owner = await bot.getch_user(bot.owner_id)
    print("Set bot variables")

    # db stuff
    bot.db = await aiosqlite.connect("dbs/db.sqlite3")
    bot.grinders_db = DatabaseHandlers.GrinderDatabaseHandler(bot)
    print("Setup DB")

    # cogs
    for extension in cogs:
        try:
            bot.load_extension(extension)
            print(f"Successfully loaded extension {extension}")
        except Exception as e:
            exc = f"{type(e).__name__,}: {e}"
            print(f"Failed to load extension {extension}\n{exc}")

        await bot.sync_application_commands(guild_id=bot.guild.id)

    print("Synced slash commands")
    await bot.owner.send("All Ready")
    print("All Ready")

bot.config = Config("config.json")
bot.loop.create_task(startup())
bot.run(bot.config.get("token"))