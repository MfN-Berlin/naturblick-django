import sqlite3
import tempfile
from pathlib import Path

import requests

from species.models import LeichtPortrait

def insert_current_version(sqlite_cursor):
    url = "http://playback:9000/speciesdbversion"
    response = requests.get(url)
    if response.status_code == 200:
        sqlite_cursor.execute("INSERT INTO species_current_version VALUES (?, ?);", (1, response.json()["version"]))
    else:
        logger.error(f"Playback not available: response [ {response.text} ]")


def leicht_portrait():
    return LeichtPortrait.objects.all()


def leicht_species():
    return [lp.species for lp in leicht_portrait()]


def insert_species(sqlite_cursor):
    sqlite_cursor.executemany(
        "INSERT INTO species VALUES (?, ?, ?);",
        ((species.id, species.gername, Path(species.avatar.image.url).name)
         for species in leicht_species())
    )


def insert_portrait(sqlite_cursor):
    sqlite_cursor.executemany(
        "INSERT INTO portrait VALUES (?, ?, ?);",
        ((portrait.species.id,
          "#".join(portrait.leichtrecognize_set.all().order_by("ordering").values_list("text", flat=True)),
          "#".join(portrait.leichtgoodtoknow_set.all().order_by("ordering").values_list("text", flat=True)))
         for portrait in leicht_portrait())
    )


def create_tables(sqlite_cursor):
    sqlite_cursor.execute(
        "CREATE TABLE IF NOT EXISTS `species_current_version` (`rowid` INTEGER NOT NULL," +
        "`version` INTEGER NOT NULL, PRIMARY KEY(`rowid`));"
    )
    sqlite_cursor.execute(
        """CREATE TABLE IF NOT EXISTS `species` (`rowid` INTEGER NOT NULL, `name` TEXT NOT NULL, `image_url` TEXT NOT NULL, PRIMARY KEY(`rowid`));"""
    )
    sqlite_cursor.execute(
        """CREATE TABLE IF NOT EXISTS `portrait` (`species_id` INTEGER NOT NULL,
            `recognize` TEXT NOT NULL,
            `good_to_know` TEXT NOT NULL,
            PRIMARY KEY(`species_id`),
            FOREIGN KEY(`species_id`) REFERENCES `species`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE 
            );"""
    )


def create_leicht_db():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    insert_current_version(sqlite_cursor)
    insert_species(sqlite_cursor)
    insert_portrait(sqlite_cursor)
    sqlite_conn.commit()
    sqlite_conn.close()

    return temp_file.name
