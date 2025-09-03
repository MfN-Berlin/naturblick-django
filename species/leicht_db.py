import sqlite3
import tempfile
import requests

def insert_current_version(sqlite_cursor):
    url = "http://playback:9000/speciesdbversion"
    response = requests.get(url)
    if response.status_code == 200:
        sqlite_cursor.execute("INSERT INTO species_current_version VALUES (?, ?);", (1, response.json()["version"]))
    else:
        logger.error(f"Playback not available: response [ {response.text} ]")

def create_tables(sqlite_cursor):
    sqlite_cursor.execute(
        "CREATE TABLE IF NOT EXISTS `species_current_version` (`rowid` INTEGER NOT NULL," +
        "`version` INTEGER NOT NULL, PRIMARY KEY(`rowid`));"
    )

def create_leicht_db():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    insert_current_version(sqlite_cursor)

    sqlite_conn.commit()
    sqlite_conn.close()

    return temp_file.name


