import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sessions import session_manager
import logging

from sessions.SessionError import SessionError, MaxSessionsError, UserHasSessionError

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("discord_bot")

token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("DISCORD_TOKEN environment variable not set")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_command(ctx):
    logger.info(f"Command used: {ctx.command} by {ctx.author} in {ctx.guild}/{ctx.channel}")

# Commands begin

@bot.hybrid_command(name="ping", with_app_command=True, description="Ping Bot and response with Pong.")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.hybrid_command(name="session start", with_app_command=True, description="Start a session.")
async def start_session(ctx):
    result = session_manager.start_session(ctx.author.id, ctx.author.name)
    if result is MaxSessionsError:
        await ctx.send("Max. number of sessions reached, too many users atm. Please try again later.")
        return
    if result is UserHasSessionError:
        await ctx.send("You already have a running session!")
        return

    ctx.send("Your session has started.")

@bot.hybrid_command(name="session stop", with_app_command=True, description="Start the running session.")
async def stop_session(ctx):
    session_manager.stop_session(ctx.author.id)
    ctx.send("Your session has started.")

# Commands end

@bot.event
async def on_ready():
    await bot.tree.sync()
    logger.info(f"Bot is online as {bot.user}")

bot.run(token)