import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sessions import session_manager
import logging


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
    session_manager.start_session(ctx.author.id, )

@bot.hybrid_command(name="session stop", with_app_command=True, description="Start the running session.")
async def stop_session(ctx):
    session_manager.stop_session(ctx.author.id)

# Commands end

@bot.event
async def on_ready():
    await bot.tree.sync()
    logger.info(f"Bot is online as {bot.user}")

bot.run(token)