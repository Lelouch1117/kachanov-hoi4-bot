games = {}
game_counter = 1


def add_game(description):
    global game_counter
    games[game_counter] = description
    game_counter += 1
    return game_counter - 1


def remove_game(game_id):
    if game_id in games:
        del games[game_id]
        return True
    return False


def list_all_games():
    if not games:
        return "Активных игр нет."

    text = ""
    for game_id, desc in games.items():
        text += f"ID {game_id}: {desc}\n\n"
    return text