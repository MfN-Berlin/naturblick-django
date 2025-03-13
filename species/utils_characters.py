import sqlite3
from pathlib import Path


def insert_characters(sqlite_cursor):
    base_dir = Path(__file__).resolve().parent.parent
    sqlite_db = base_dir / 'species' / 'data' / 'characters.sqlite'
    conn = sqlite3.connect(sqlite_db)
    char_cursor = conn.cursor()

    data = [a for a in char_cursor.execute("SELECT * FROM character")]
    sqlite_cursor.executemany("INSERT INTO character VALUES (?, ?, ?, ?, ?, ?, ? ,?)", data)

    data = [a for a in char_cursor.execute("SELECT * FROM character_value")]
    sqlite_cursor.executemany("INSERT INTO character_value VALUES (?, ?, ?, ?, ?)", data)

    data = [a for a in char_cursor.execute("SELECT * FROM character_value_species")]
    sqlite_cursor.executemany("INSERT INTO character_value_species VALUES (?, ?, ?, ?, ?)",
                              data)

    conn.close()
