from datetime import timedelta
import sqlite3
import csv
import logging


logger = logging.getLogger(__name__)

def init_db():
    """
    Create the database and tables if they don't exist, and populate 
    the friends table from a CSV file.
    """
    logger.debug("Initializing the database...")
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
    logger.debug("Populating the friends table from friends.csv...")
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

def insert_message(email, subject, body_plain, body_html):
    """
    Insert a new message into the database.
    """
    logger.debug("Inserting a new message into the database.")
    conn = sqlite3.connect("friendslist.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM friends WHERE email = ?", (email,))
    friend_row = cur.fetchone()
    if not friend_row:
        conn.close()
        raise ValueError(f"No friend found with email: {email}")

    friend_id = friend_row[0]
    cur.execute(
        "INSERT INTO messages (friend_id, subject, body_plain, body_html) VALUES (?, ?, ?, ?)",
        (friend_id, subject, body_plain, body_html),
    )
    conn.commit()
    conn.close()


def get_all_messages_for_fortnight(datetime):
    """
    Retrieve all messages received between the given date and two weeks before it.
    """

    conn = sqlite3.connect("friendslist.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT f.name, f.email, m.subject, m.body_plain, m.body_html, m.received_at
        FROM messages m
        JOIN friends f ON m.friend_id = f.id
        WHERE m.received_at BETWEEN ? AND ?
        ORDER BY m.received_at DESC
    """, (datetime - timedelta(days=14), datetime))
