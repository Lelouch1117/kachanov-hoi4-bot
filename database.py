import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

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
