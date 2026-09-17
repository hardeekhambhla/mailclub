import sqlite3

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS waitlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def add_to_waitlist(email):
    with get_conn() as conn:
        conn.execute("INSERT INTO waitlist (email) VALUES (?) ON CONFLICT(email) DO NOTHING", (email,))


def waitlist_count():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM waitlist").fetchone()["n"]
