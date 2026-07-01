import sqlite3
import csv


def init_db():
    conn = sqlite3.connect("friendslist.db")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

    with open("friends.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row

        cur.executemany(
            "INSERT OR IGNORE INTO friends (name, email) VALUES (?, ?);",
            csv_reader,
        )

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            friend_id INTEGER REFERENCES friends(id),
            subject TEXT NOT NULL,
            body_plain TEXT,
            body_html TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def friend_exists(email):
    conn = sqlite3.connect("friendslist.db")
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM friends WHERE email = ?", (email,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists
