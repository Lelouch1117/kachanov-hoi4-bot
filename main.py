import os
import discord
from discord.ext import commands
from discord import app_commands

from database import init_db, get_games, add_game, delete_game
import countries

# ---------------- INIT ----------------

print("DEBUG DATABASE_URL =", os.getenv("DATABASE_URL"))

init_db()

TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise ValueError("TOKEN не найден")

GUILD_ID = 1352318286788038746

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- READY ----------------

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Бот запущен как {bot.user}")

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("Команды пересинхронизированы")
    print(f"Бот запущен как {bot.user}")

# ---------------- GAMES (через БД) ----------------

@bot.tree.command(name="add_game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(description="Описание игры")
async def add_game_command(interaction: discord.Interaction, description: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    game_id = add_game(description)
    await interaction.response.send_message(f"Игра добавлена с ID {game_id}")


@bot.tree.command(name="list_games", guild=discord.Object(id=GUILD_ID))
async def list_games_command(interaction: discord.Interaction):

    games = get_games()

    if not games:
        await interaction.response.send_message("Активных игр нет.")
        return

    text = ""
    for game in games:
        text += f"ID {game['id']}: {game['description']}\n\n"

    await interaction.response.send_message(text)


@bot.tree.command(name="clear_game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(game_id="ID игры")
async def clear_game_command(interaction: discord.Interaction, game_id: int):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    delete_game(game_id)
    await interaction.response.send_message("Игра удалена (если существовала).")

# ---------------- RUN ----------------

bot.run(TOKEN)



