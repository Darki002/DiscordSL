import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from sessions import session_manager
import logging
import asyncio

from sessions.SessionError import MaxSessionsError, UserHasSessionError, SessionError
from sessions.podman_check import check_podman_socket

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("discord_bot")

uid = os.geteuid()
gid = os.getegid()
logger.info(f"Bot running as UID {uid}, GID {gid}")

if not check_podman_socket():
    logger.warning("Podman socket check failed. Bot will not function properly.")
    exit(77)

token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("DISCORD_TOKEN environment variable not set")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

status_messages = {}

async def monitor_container_status():
    while True:
        for user_id, (message, session) in list(status_messages.items()):
            status = session.status()
            if status == "running":
                await message.edit(content="Your session is ready!")
                del status_messages[user_id]
            elif status in ["exited", "error"]:
                await message.edit(content="Failed to start your session. Please try again later.")
                del status_messages[user_id]
            else:
                await message.edit(content=f"Your session is {status}...")
        await asyncio.sleep(5) # 5sec delay -> prevent the CPU from being occupied for no reason all the time


# Discord has a limit of 2000 Character, we trim to 1900, because of the Markdown formating characters we add later on.
def trim_output(text: str, limit: int = 1900) -> str:
    """Trim output to avoid hitting Discord's 2000 character limit."""
    if len(text) > limit:
        return text[:limit] + "\n... (truncated)"
    return text


@bot.event
async def on_command(ctx: commands.Context):
    logger.info(f"Command used: {ctx.command} by {ctx.author} in {ctx.guild}/{ctx.channel}")

# Commands begin

@bot.hybrid_command(name="ping", with_app_command=True, description="Ping Bot and response with Pong.")
async def ping(ctx: commands.Context):
    await ctx.send("Pong!")


@bot.hybrid_command(name="start", with_app_command=True, description="Start a session.")
async def start_session(ctx: commands.Context):
    result = session_manager.start_session(ctx.author.id, ctx.author.name)

    if isinstance(result, MaxSessionsError):
        await ctx.send("Max. number of sessions reached…")
        return
    if isinstance(result, UserHasSessionError):
        await ctx.send("You already have a running session!")
        return
    if isinstance(result, SessionError):
        await ctx.send("Whoops! Unexpected error while starting a session!")
        return

    message = await ctx.send("Your session is starting...")
    status_messages[result.user_id] = (message, result)


@bot.hybrid_command(name="stop", with_app_command=True, description="Stop the running session.")
async def stop_session(ctx: commands.Context):
    session_manager.stop_session(ctx.author.id)
    await ctx.send("Your session has stoped.")


@bot.hybrid_command(name="status", with_app_command=True, description="Checks the status of the session.")
async def session_status(ctx: commands.Context):
    status = session_manager.get_container_status(ctx.author.id)
    await ctx.send(f"Your session is {status}!")


@bot.hybrid_command(name="exec", with_app_command=True, description="Executes a bash command within your current session.")
@app_commands.describe(command="The bash command you want to run")
async def exec_bash(ctx: commands.Context, command: str):
    session = session_manager.get_session(ctx.author.id)
    if session is None:
        await ctx.send("You have no active session. You can start one with `/start`")
        return

    stdout, stderr = session.exec_bash(command)

    response = ""
    if stdout:
        stdout_trim = trim_output(stdout)
        response += f"**STDOUT:**\n```bash\n{stdout_trim}\n```"
    if stderr:
        stderr_trim = trim_output(stderr)
        response += f"**STDERR:**\n```bash\n{stderr_trim}\n```"
    if not response:
        response = "No output was returned."

    await ctx.send(response)


# Commands end
@bot.event
async def on_ready():
    await bot.tree.sync()

    logger.info(f"Bot is online as {bot.user}")
    bot.loop.create_task(monitor_container_status())

bot.run(token)
