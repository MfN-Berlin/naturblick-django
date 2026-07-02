import sqlite3
import tempfile

from species.models import LeichtPortrait


def leicht_portrait():
    return LeichtPortrait.objects.all()


def insert_portrait(sqlite_cursor):
    sqlite_cursor.executemany(
        "INSERT INTO portrait VALUES (?, ?, ?, ?, ?);",
        ((portrait.id,
          portrait.name,
          "#".join(
              portrait.leichtdescription_set.all()
              .order_by("ordering")
              .values_list("text", flat=True)
          ),
          portrait.location,
          portrait.initially_visible)
         for portrait in leicht_portrait())
    )


def create_tables(sqlite_cursor):
    sqlite_cursor.execute(
        """CREATE TABLE IF NOT EXISTS `portrait` (`rowid` INTEGER NOT NULL, `name` TEXT NOT NULL, `description` TEXT NOT NULL, `location` TEXT NOT NULL, `initially_visible` INTEGER NOT NULL, PRIMARY KEY(`rowid`));"""
    )


def create_leicht_db():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    insert_portrait(sqlite_cursor)
    sqlite_conn.commit()
    sqlite_cursor.execute("VACUUM;")
    sqlite_conn.close()

    return temp_file.name
