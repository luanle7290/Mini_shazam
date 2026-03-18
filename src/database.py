"""
Database Module (SQLite)
Stores song metadata and audio fingerprints.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fingerprints.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS songs (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            artist  TEXT,
            file    TEXT
        );

        CREATE TABLE IF NOT EXISTS fingerprints (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            hash    TEXT NOT NULL,
            offset  INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            FOREIGN KEY (song_id) REFERENCES songs(id)
        );

        CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints(hash);

        CREATE TABLE IF NOT EXISTS history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id         INTEGER NOT NULL,
            title           TEXT NOT NULL,
            artist          TEXT,
            recognized_at   TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
    """)
    conn.commit()
    conn.close()
    print("[DB] Database initialised.")


def insert_song(title: str, artist: str = "", file: str = "") -> int:
    """Insert a song record and return its id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO songs (title, artist, file) VALUES (?, ?, ?)",
        (title, artist, file)
    )
    song_id = cur.lastrowid
    conn.commit()
    conn.close()
    return song_id


def insert_fingerprints(hashes: list):
    """
    Bulk-insert fingerprints.
    hashes: list of (hash_str, time_offset, song_id)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO fingerprints (hash, offset, song_id) VALUES (?, ?, ?)",
        hashes
    )
    conn.commit()
    conn.close()


def query_hashes(hash_list: list) -> list:
    """
    Look up a list of hashes and return matching rows.
    Returns list of (hash, offset, song_id, title, artist).
    """
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ','.join('?' * len(hash_list))
    cur.execute(f"""
        SELECT f.hash, f.offset, f.song_id, s.title, s.artist
        FROM fingerprints f
        JOIN songs s ON f.song_id = s.id
        WHERE f.hash IN ({placeholders})
    """, hash_list)
    rows = cur.fetchall()
    conn.close()
    return rows


def list_songs() -> list:
    """Return all songs in the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, artist, file FROM songs ORDER BY title")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_song(song_id: int):
    """Delete a song and all its fingerprints from the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM fingerprints WHERE song_id = ?", (song_id,))
    cur.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()


def log_recognition(song_id: int, title: str, artist: str):
    """Record a successful recognition in history."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (song_id, title, artist) VALUES (?, ?, ?)",
        (song_id, title, artist)
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 50) -> list:
    """Return the most recent recognitions."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT title, artist, recognized_at FROM history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def song_count() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM songs")
    count = cur.fetchone()[0]
    conn.close()
    return count
