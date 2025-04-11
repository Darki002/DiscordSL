import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("DISCORD_TOKEN environment variable not set")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_command(ctx):
    print(f"Command used: {ctx.command} by {ctx.author} in {ctx.guild}/{ctx.channel}")


@bot.hybrid_command(name="ping", with_app_command=True, description="Antwortet mit Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_ready():
    await bot.tree.sync()  # Synchronisiert die Slash-Befehle mit Discord
    print(f"Bot ist online als {bot.user}")

bot.run(token)