import os
import discord
from discord.ext import commands
from discord import app_commands

from database import (
    init_db,
    add_game_db,
    get_games,
    remove_game_db
)
import countries


# ================= INIT =================

print("DEBUG DATABASE_URL =", os.getenv("DATABASE_URL"))

init_db()

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


# =====================================================
# ======================= GAMES ========================
# =====================================================

@bot.tree.command(name="add_game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(description="Описание игры")
async def add_game(interaction: discord.Interaction, description: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    game_id = add_game_db(description)
    await interaction.response.send_message(f"Игра добавлена с ID {game_id}")


@bot.tree.command(name="list_games", guild=discord.Object(id=GUILD_ID))
async def list_games(interaction: discord.Interaction):

    db_games = get_games()

    if not db_games:
        await interaction.response.send_message("Активных игр нет.")
        return

    text = ""
    for game in db_games:
        text += f"ID {game['id']}: {game['description']}\n\n"

    await interaction.response.send_message(text)


@bot.tree.command(name="clear_game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(game_id="ID игры")
async def clear_game(interaction: discord.Interaction, game_id: int):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    if remove_game_db(game_id):
        await interaction.response.send_message("Игра удалена.")
    else:
        await interaction.response.send_message("Игра не найдена.", ephemeral=True)


# =====================================================
# ===================== COUNTRIES ======================
# =====================================================

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

    available = countries.get_available_countries()

    if not available:
        await interaction.response.send_message("Свободных стран нет.")
        return

    # Если стран больше 25 — выводим списком
    if len(available) > 25:
        text = ", ".join(available)
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

@bot.tree.command(name="register", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(tag="Тег страны (например SOV)")
async def register(interaction: discord.Interaction, tag: str):

    tag = tag.upper()

    result = countries.assign_country(tag, interaction.user.id)

    if result == "taken":
        await interaction.response.send_message("Эта страна занята.", ephemeral=True)
        return

    if result == "not_found":
        await interaction.response.send_message("Страна не найдена.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"{interaction.user.display_name} занял {tag}"
    )

    try:
        await interaction.user.send(f"Вы успешно заняли {tag}")
    except:
        pass
# =====================================================
# ===================== ADMIN PANEL ====================
# =====================================================

class AdminPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Список занятых стран", style=discord.ButtonStyle.secondary)
    async def show_taken(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Нет прав.", ephemeral=True)
            return

        taken = countries.get_taken_countries()

        if not taken:
            await interaction.response.send_message("Никто не зарегистрирован.", ephemeral=True)
            return

        text = ""
        for row in taken:
            tag = row["tag"]
            user_id = row["user_id"]

            try:
                member = await interaction.guild.fetch_member(user_id)
                name = member.display_name
            except:
                name = f"ID {user_id}"

            text += f"{tag} — {name}\n"

        await interaction.response.send_message(text, ephemeral=True)


@bot.tree.command(name="admin_panel", guild=discord.Object(id=GUILD_ID))
async def admin_panel(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Нет прав.", ephemeral=True)
        return

    view = AdminPanel()
    await interaction.response.send_message("Админ-панель:", view=view, ephemeral=True)

# ================= RUN =================

bot.run(TOKEN)




