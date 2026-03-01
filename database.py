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
