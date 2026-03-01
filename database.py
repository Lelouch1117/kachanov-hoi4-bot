import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id SERIAL PRIMARY KEY,
        description TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        tag VARCHAR(10) PRIMARY KEY,
        user_id BIGINT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
def add_game(description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO games (description) VALUES (%s) RETURNING id;", (description,))
    game_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return game_id


def get_games():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games ORDER BY id;")
    games = cur.fetchall()
    cur.close()
    conn.close()
    return games


def delete_game(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM games WHERE id = %s;", (game_id,))
    conn.commit()
    cur.close()
    conn.close()
def set_countries(tags):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM countries;")
    for tag in tags:
        cur.execute("INSERT INTO countries (tag, user_id) VALUES (%s, NULL);", (tag,))
    conn.commit()
    cur.close()
    conn.close()


def get_available_countries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tag FROM countries WHERE user_id IS NULL;")
    countries = [row["tag"] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return countries


def register_country(tag, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM countries WHERE tag = %s;", (tag,))
    result = cur.fetchone()

    if not result:
        cur.close()
        conn.close()
        return "NOT_FOUND"

    if result["user_id"] is not None:
        cur.close()
        conn.close()
        return "TAKEN"

    cur.execute("UPDATE countries SET user_id = %s WHERE tag = %s;", (user_id, tag))
    conn.commit()
    cur.close()
    conn.close()
    return "SUCCESS"


def clear_countries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM countries;")
    conn.commit()
    cur.close()
    conn.close()
def register_country(tag, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO countries (tag, user_id) VALUES (%s, %s) ON CONFLICT (tag) DO UPDATE SET user_id = EXCLUDED.user_id",
        (tag, user_id)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_taken_countries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM countries")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
def add_game_db(description):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO games (description) VALUES (%s) RETURNING id",
        (description,)
    )

    game_id = cur.fetchone()["id"]

    conn.commit()
    cur.close()
    conn.close()

    return game_id


def get_games():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, description FROM games ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def remove_game_db(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM games WHERE id = %s", (game_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return deleted > 0
def assign_country(tag, user_id):
    conn = get_connection()
    cur = conn.cursor()

    # Проверяем существует ли страна
    cur.execute("SELECT user_id FROM countries WHERE tag = %s", (tag,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return "not_found"

    # Если уже занята другим
    if row["user_id"] and row["user_id"] != user_id:
        cur.close()
        conn.close()
        return "taken"

    # Убираем старую страну у пользователя
    cur.execute("UPDATE countries SET user_id = NULL WHERE user_id = %s", (user_id,))

    # Назначаем новую
    cur.execute(
        "UPDATE countries SET user_id = %s WHERE tag = %s",
        (user_id, tag)
    )

    conn.commit()
    cur.close()
    conn.close()

    return "ok"
