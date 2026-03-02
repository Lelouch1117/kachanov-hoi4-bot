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

@bot.tree.command(name="help", guild=discord.Object(id=GUILD_ID))
async def help_command(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📘 Помощь по боту",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🎮 Игрокам",
        value="""
/list_countries — список стран  
/register TAG — занять страну  
""",
        inline=False
    )

    embed.add_field(
        name="🛠 Администраторам",
        value="""
/enter_countries — добавить страны  
/clear_countries — очистить  
/admin_panel — панель управления  
/open_registration — открыть панель регистрации  
""",
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)
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

    # Если мало стран → кнопки
    if len(available) <= 10:
        view = countries.CountryView()
        await interaction.response.send_message(
            "Выберите страну:",
            view=view
        )
        return

    # Если много стран → список
    text = ", ".join(available)

    await interaction.response.send_message(
        f"Свободные страны:\n{text}\n\nИспользуйте /register TAG"
    )


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

@bot.tree.command(name="open_registration", guild=discord.Object(id=GUILD_ID))
class RegistrationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        available = countries.get_available_countries()

        # Кнопки только если <=25
        if len(available) <= 25:
            for tag in available:
                self.add_item(RegisterButton(tag))


class RegisterButton(discord.ui.Button):
    def __init__(self, tag):
        super().__init__(label=tag, style=discord.ButtonStyle.primary)
        self.tag = tag

    async def callback(self, interaction: discord.Interaction):

        result = countries.assign_country(self.tag, interaction.user.id)

        if result == "taken":
            await interaction.response.send_message("Страна занята.", ephemeral=True)
            return

        if result == "not_found":
            await interaction.response.send_message("Страна не найдена.", ephemeral=True)
            return

        await interaction.response.defer()

        # Обновляем панель
        await update_registration_panel(interaction)

async def update_registration_panel(interaction):

    available = countries.get_available_countries()
    taken = countries.get_taken_countries()

    embed = discord.Embed(
        title="🎮 Регистрация на игру",
        color=discord.Color.blue()
    )

    if available:
        embed.add_field(
            name="🟢 Свободные страны",
            value="\n".join(available),
            inline=False
        )
    else:
        embed.add_field(
            name="🟢 Свободные страны",
            value="Нет",
            inline=False
        )

    if taken:
    text = ""

    for row in taken:
        tag = row["tag"]
        user_id = row["user_id"]
        text += f"{tag} — <@{user_id}>\n"

    embed.add_field(
        name="🔴 Занятые страны",
        value=text,
        inline=False
    )
    else:
        embed.add_field(
            name="🔴 Занятые страны",
            value="Нет",
            inline=False
        )

    view = RegistrationView()

    await interaction.message.edit(embed=embed, view=view)

@bot.tree.command(name="open_registration", guild=discord.Object(id=GUILD_ID))
async def open_registration(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎮 Регистрация на игру",
        description="Выберите страну кнопкой или используйте /register TAG",
        color=discord.Color.green()
    )

    view = RegistrationView()

    await interaction.response.send_message(embed=embed, view=view)
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
    text += f"{tag} — <@{user_id}>\n"

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

@discord.ui.button(label="❌ Убрать игрока", style=discord.ButtonStyle.danger)

# ================= RUN =================

bot.run(TOKEN)









