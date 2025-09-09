import sqlite3
import tempfile
from pathlib import Path

import requests
from species.models import Species

def insert_current_version(sqlite_cursor):
    url = "http://playback:9000/speciesdbversion"
    response = requests.get(url)
    if response.status_code == 200:
        sqlite_cursor.execute("INSERT INTO species_current_version VALUES (?, ?);", (1, response.json()["version"]))
    else:
        logger.error(f"Playback not available: response [ {response.text} ]")

def leicht_species():
    return Species.objects.filter(
        portrait__language__exact='dels',
        avatar__isnull=False,
        gername__isnull=False
    )

def insert_species(sqlite_cursor):
        sqlite_cursor.executemany(
            "INSERT INTO species VALUES (?, ?, ?);",
            ((species.id, species.gername, Path(species.avatar.image.url).name)
             for species in leicht_species())
        )

def create_tables(sqlite_cursor):
    sqlite_cursor.execute(
        "CREATE TABLE IF NOT EXISTS `species_current_version` (`rowid` INTEGER NOT NULL," +
        "`version` INTEGER NOT NULL, PRIMARY KEY(`rowid`));"
    )
    sqlite_cursor.execute(
        """CREATE TABLE IF NOT EXISTS `species` (`rowid` INTEGER NOT NULL, `name` TEXT NOT NULL, `image_url` TEXT NOT NULL, PRIMARY KEY(`rowid`));"""
    )

def create_leicht_db():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    insert_current_version(sqlite_cursor)
    insert_species(sqlite_cursor)
    sqlite_conn.commit()
    sqlite_conn.close()

    return temp_file.name

