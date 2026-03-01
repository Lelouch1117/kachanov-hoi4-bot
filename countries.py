import discord

available_countries = []
taken_countries = {}   # tag -> user_id
user_country = {}      # user_id -> tag


def set_countries(countries_string):
    global available_countries, taken_countries, user_country
    available_countries = [c.strip().upper() for c in countries_string.split(",")]
    taken_countries.clear()
    user_country.clear()


def clear_all():
    available_countries.clear()
    taken_countries.clear()
    user_country.clear()


class CountryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        for tag in available_countries:
            self.add_item(CountryButton(tag))


class CountryButton(discord.ui.Button):
    def __init__(self, tag):
        super().__init__(label=tag, style=discord.ButtonStyle.primary)
        self.tag = tag

    async def callback(self, interaction: discord.Interaction):

        tag = self.tag
        user_id = interaction.user.id

        # Если страна занята другим
        if tag in taken_countries and taken_countries[tag] != user_id:
            await interaction.response.send_message("Эта страна занята.", ephemeral=True)
            return

        # Если пользователь уже выбрал страну
        if user_id in user_country:
            old_tag = user_country[user_id]
            if old_tag != tag:
                available_countries.append(old_tag)
                del taken_countries[old_tag]

        # Назначаем новую
        taken_countries[tag] = user_id
        user_country[user_id] = tag

        if tag in available_countries:
            available_countries.remove(tag)

        await interaction.response.send_message(f"Вы заняли {tag}")

        try:
            await interaction.user.send(f"Вы успешно заняли {tag}")
        except:
            pass

        # Обновляем панель
        await interaction.message.edit(view=CountryView())