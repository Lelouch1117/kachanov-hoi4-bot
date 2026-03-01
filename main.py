from database import init_db
init_db()
import os
import discord
from discord.ext import commands
from discord import app_commands
import countries
import games

TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise ValueError("TOKEN не найден в переменных окружения")
GUILD_ID = 1352318286788038746

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Бот запущен как {bot.user}")


# ----------------- COUNTRIES -----------------

@bot.tree.command(name="enter_countries", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(countries_list="Введите через запятую: SOV,GER,USA")
async def enter_countries(interaction: discord.Interaction, countries_list: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    countries.set_countries(countries_list)
    await interaction.response.send_message("Список стран обновлён.")


@bot.tree.command(name="list_countries", guild=discord.Object(id=GUILD_ID))
async def list_countries(interaction: discord.Interaction):

    if not countries.available_countries:
        await interaction.response.send_message("Свободных стран нет.")
        return

    # Если стран больше 25 — выводим списком
    if len(countries.available_countries) > 25:
        text = ", ".join(countries.available_countries)
        await interaction.response.send_message(
            f"Свободные страны:\n{text}\n\nИспользуйте /register TAG"
        )
        return

    # Если <=25 — показываем кнопки
    view = countries.CountryView()
    await interaction.response.send_message("Выберите страну:", view=view)


@bot.tree.command(name="clear_countries", guild=discord.Object(id=GUILD_ID))
async def clear_countries(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    countries.clear_all()
    await interaction.response.send_message("Список стран очищен.")


# ----------------- GAMES -----------------

@bot.tree.command(name="add_game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(description="Описание игры")
async def add_game(interaction: discord.Interaction, description: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    game_id = games.add_game(description)
    await interaction.response.send_message(f"Игра добавлена с ID {game_id}")


@bot.tree.command(name="list_games", guild=discord.Object(id=GUILD_ID))
async def list_games(interaction: discord.Interaction):

    if not games.games:
        await interaction.response.send_message("Активных игр нет.")
        return

    text = ""
    for game_id, desc in games.games.items():
        text += f"ID {game_id}: {desc}\n\n"

    await interaction.response.send_message(text)


@bot.tree.command(name="clear_game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(game_id="ID игры")
async def clear_game(interaction: discord.Interaction, game_id: int):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    if games.remove_game(game_id):
        await interaction.response.send_message("Игра удалена.")
    else:
        await interaction.response.send_message("Игра не найдена.", ephemeral=True)


# ----------------- ADMIN PANEL -----------------

class AdminPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Список занятых стран", style=discord.ButtonStyle.secondary)
    async def show_taken(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Нет прав.", ephemeral=True)
            return

        if not countries.taken_countries:
            await interaction.response.send_message("Никто не зарегистрирован.", ephemeral=True)
            return

        text = ""
        for tag, user_id in countries.taken_countries.items():
            user = await interaction.guild.fetch_member(user_id)
            text += f"{tag} — {user.display_name}\n"

        await interaction.response.send_message(text, ephemeral=True)


@bot.tree.command(name="admin_panel", guild=discord.Object(id=GUILD_ID))
async def admin_panel(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    view = AdminPanel()
    await interaction.response.send_message("Админ-панель:", view=view, ephemeral=True)



bot.run(TOKEN)

