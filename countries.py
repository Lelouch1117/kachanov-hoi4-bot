import discord
from database import (
    assign_country,
    get_available_countries,
    get_taken_countries
)


# =====================================================
# ======================= UI ==========================
# =====================================================

class CountryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        available = get_available_countries()

        for tag in available:
            self.add_item(CountryButton(tag))


class CountryButton(discord.ui.Button):
    def __init__(self, tag):
        super().__init__(label=tag, style=discord.ButtonStyle.primary)
        self.tag = tag

    async def callback(self, interaction: discord.Interaction):

        result = assign_country(self.tag, interaction.user.id)

        if result == "taken":
            await interaction.response.send_message(
                "Эта страна занята.",
                ephemeral=True
            )
            return

        if result == "not_found":
            await interaction.response.send_message(
                "Страна не найдена.",
                ephemeral=True
            )
            return

        # Публичное сообщение
        await interaction.response.send_message(
            f"{interaction.user.mention} занял {self.tag}"
        )

        # ЛС игроку
        try:
            await interaction.user.send(f"Вы успешно заняли {self.tag}")
        except:
            pass

        # Обновляем кнопки
        await interaction.message.edit(view=CountryView())
