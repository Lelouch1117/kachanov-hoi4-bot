import discord
from database import get_connection


# ----------------- DB FUNCTIONS -----------------

def set_countries(countries_string):
    tags = [c.strip().upper() for c in countries_string.split(",")]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM countries")

    for tag in tags:
        cur.execute(
            "INSERT INTO countries (tag, user_id) VALUES (%s, NULL)",
            (tag,)
        )

    conn.commit()
    cur.close()
    conn.close()


def clear_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM countries")
    conn.commit()
    cur.close()
    conn.close()


def get_available_countries():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT tag FROM countries
        WHERE user_id IS NULL
        ORDER BY tag
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [row["tag"] for row in rows]


def get_taken_country_by_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tag FROM countries WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["tag"] if row else None
    
def get_taken_countries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tag, user_id FROM countries WHERE user_id IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def assign_country(tag, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM countries WHERE tag = %s", (tag,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return "not_found"

    if row["user_id"] and row["user_id"] != user_id:
        cur.close()
        conn.close()
        return "taken"

    # Освобождаем старую страну пользователя
    cur.execute("UPDATE countries SET user_id = NULL WHERE user_id = %s", (user_id,))

    # Назначаем новую
    cur.execute("UPDATE countries SET user_id = %s WHERE tag = %s", (user_id, tag))

    conn.commit()
    cur.close()
    conn.close()

    return "ok"

async def callback(self, interaction: discord.Interaction):

    await interaction.response.defer()   # <-- ДОБАВЬ ЭТУ СТРОКУ

    result = assign_country(self.tag, interaction.user.id)
# ----------------- UI -----------------

class CountryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        for tag in get_available_countries():
            self.add_item(CountryButton(tag))


async def callback(self, interaction: discord.Interaction):

    await interaction.response.defer()

    result = assign_country(self.tag, interaction.user.id)

    if result == "taken":
        await interaction.followup.send("Эта страна занята.", ephemeral=True)
        return

    if result == "not_found":
        await interaction.followup.send("Страна не найдена.", ephemeral=True)
        return

    # Публичное сообщение
    await interaction.followup.send(
        f"{interaction.user.display_name} занял {self.tag}"
    )

    # Личное сообщение
    try:
        await interaction.user.send(f"Вы успешно заняли {self.tag}")
    except:
        pass

    await interaction.message.edit(view=CountryView())





