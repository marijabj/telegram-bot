import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username TEXT
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

def add_user(user_id, username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (user_id, username) VALUES (%s,%s) ON CONFLICT DO NOTHING",
        (user_id, username)
    )
    conn.commit()
    cur.close()
    conn.close()

def user_exists(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id=%s", (user_id,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

