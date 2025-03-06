import logging
import sqlite3
import tempfile

from species.models import Species, SpeciesName, PortraitImageFile, Faunaportrait


#
#
#
#   INSERT ALL SPECIES !!
#
#
#
#

logger = logging.getLogger(__name__)

def insert_portrait_image_and_sizes(sqlite_cursor):
    #TODO johannes: text fehlt '' -> War bisher sprachlos, ist jetzt aber je Sprache setzbar.
    id = 1
    for fp in list(Faunaportrait.objects.all()):

        if hasattr(fp, 'descmeta'):
            text = fp.descmeta.text
            pif = fp.descmeta.portrait_image_file
            sqlite_cursor.execute("INSERT INTO portrait_image VALUES (?, ?, ?, ?, ?, ?)", (id, pif.owner, pif.owner_link, pif.source, text, pif.license))

            sqlite_cursor.execute("INSERT INTO portrait_image_size VALUES (?, ?, ? ,?)",
                                  (id, width, height, url))

            id += 1

    # data = list(map(lambda pif: (pif.id, pif.owner, pif.owner_link, pif.source, '', pif.license), PortraitImageFile.objects.all()))
    # sqlite_cursor.executemany("INSERT INTO portrait_image VALUES (?, ?, ?, ?, ?, ?)", data)

    # TODO johannes
    # "INSERT INTO portrait_image_size VALUES (?, ?, ? ,?);"
    # setInt(1, portraitImageId)
    # setInt(2, width)
    # setInt(3, height)
    # setString(4, url)


def insert_portrait(sqlite_cursor):
    #`rowid` INTEGER NOT NULL,
    # `species_id` INTEGER NOT NULL,
    # `description` TEXT NOT NULL,
    # `description_image_id` INTEGER,
    # `language` INTEGER NOT NULL,
    # `in_the_city` TEXT NOT NULL,
    # `in_the_city_image_id` INTEGER,
    # `good_to_know_image_id` INTEGER,
    # `sources` TEXT,
    # `audio_url` TEXT,
    # `landscape` INTEGER NOT NULL,
    # `focus` REAL NOT NULL
    #"INSERT INTO portrait VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?);"
    pass


def insert_similar_species(sqlite_cursor):
    # `portrait_id` INTEGER NOT NULL, `similar_to_id` INTEGER NOT NULL, `differences` TEXT NOT NULL
    #"INSERT INTO similar_species VALUES (?, ?, ?);"
    pass


def insert_unambiguous_feature(sqlite_cursor):
    #"INSERT INTO unambiguous_feature VALUES (?, ?);"
    pass


def insert_good_to_know(sqlite_cursor):
    #"INSERT INTO good_to_know VALUES (?, ?);"
    pass


def create_sqlite_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    insert_species(sqlite_cursor)
    insert_portrait_image_and_sizes(sqlite_cursor)
    insert_portrait(sqlite_cursor)
    insert_similar_species (sqlite_cursor)
    insert_unambiguous_feature(sqlite_cursor)
    insert_good_to_know(sqlite_cursor)


    sqlite_conn.commit()
    sqlite_conn.close()

    return temp_file.name


def get_synonnyms(language, species_id):
    return ",".join(SpeciesName.objects.filter(species=species_id, language=language).values_list("name", flat=True))


def allow_break_on_hyphen(s):
    return s.replace("-", "\u200b-\u200b") if s else None


def insert_species(sqlite_cursor):
    data = list(map(map_species(),
                    Species.objects.all()[:100]))
    sqlite_cursor.executemany("INSERT INTO species VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", data)

    # could be done on insert level
    sqlite_cursor.execute("""
        UPDATE species
                    SET gersearchfield = coalesce(gername, '') || '|' || coalesce(gersynonym, '') || '|' || coalesce(sciname, ''),
                        engsearchfield = coalesce(engname, '') || '|' || coalesce(engsynonym, '') || '|' || coalesce(sciname, '')
                    WHERE accepted IS NULL OR 
                        (accepted IS NOT NULL AND NOT EXISTS (SELECT * FROM species as s2 WHERE s2.rowid = species.accepted));
        """)
    sqlite_cursor.execute("""
        UPDATE species 
        SET gersearchfield = gersearchfield || '|' || accepting.gsf,
            engsearchfield = engsearchfield || '|' || accepting.esf
        FROM (
            SELECT accepted.rowid as accepted_id, 
                coalesce(accepting.gername, '') || '|' ||  coalesce(accepting.gersynonym, '') || '|' || coalesce(accepting.sciname, '') as gsf, 
                coalesce(accepting.engname, '') || '|' || coalesce(accepting.engsynonym, '') || '|' || coalesce(accepting.sciname, '') as esf
            FROM species as accepting
            JOIN species as accepted ON accepting.accepted = accepted.rowid
            WHERE accepting.accepted IS NOT NULL
        ) AS accepting
        WHERE accepting.accepted_id = rowid;
        """)
    sqlite_cursor.execute("ALTER TABLE species DROP COLUMN accepted;")
    sqlite_cursor.execute("ALTER TABLE species DROP COLUMN gbifusagekey;")


def map_species():
    return lambda s: (
        s.id, s.group.name, allow_break_on_hyphen(s.sciname), allow_break_on_hyphen(s.gername),
        allow_break_on_hyphen(s.engname), None, None, None, get_synonnyms('de', s.id),
        get_synonnyms('en', s.id), s.red_list_germany, s.iucncategory, s.speciesid, s.gbifusagekey,
        s.accepted_species.id if s.accepted_species else None, None, None)


def create_tables(sqlite_cursor):
    sqlite_cursor.execute(
        "CREATE TABLE `species` (`rowid` INTEGER NOT NULL, `group_id` TEXT NOT NULL, `sciname` TEXT NOT NULL, `gername` TEXT, `engname` TEXT, `wikipedia` TEXT, `image_url` TEXT, `female_image_url` TEXT, `gersynonym` TEXT, `engsynonym` TEXT, `red_list_germany` TEXT, `iucn_category` TEXT, `old_species_id` TEXT NOT NULL, `gbifusagekey` INTEGER, `accepted` INTEGER, `gersearchfield` TEXT, `engsearchfield` TEXT, PRIMARY KEY(`rowid`));"
    )
    sqlite_cursor.execute("CREATE INDEX idx_species_gername ON species(gername);")
    sqlite_cursor.execute("CREATE INDEX idx_species_engname ON species(engname);")
    sqlite_cursor.execute(
        "CREATE TABLE `portrait` (`rowid` INTEGER NOT NULL, `species_id` INTEGER NOT NULL, `description` TEXT NOT NULL, `description_image_id` INTEGER, `language` INTEGER NOT NULL, `in_the_city` TEXT NOT NULL, `in_the_city_image_id` INTEGER, `good_to_know_image_id` INTEGER, `sources` TEXT, `audio_url` TEXT, `landscape` INTEGER NOT NULL, `focus` REAL NOT NULL, PRIMARY KEY(`rowid`), FOREIGN KEY(`species_id`) REFERENCES `species`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`description_image_id`) REFERENCES `portrait_image`(`rowid`) ON UPDATE NO ACTION ON DELETE SET NULL , FOREIGN KEY(`in_the_city_image_id`) REFERENCES `portrait_image`(`rowid`) ON UPDATE NO ACTION ON DELETE SET NULL , FOREIGN KEY(`good_to_know_image_id`) REFERENCES `portrait_image`(`rowid`) ON UPDATE NO ACTION ON DELETE SET NULL );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `portrait_image` (`rowid` INTEGER NOT NULL, `owner` TEXT NOT NULL, `owner_link` TEXT, `source` TEXT NOT NULL, `text` TEXT NOT NULL, `license` TEXT NOT NULL, PRIMARY KEY(`rowid`));"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `portrait_image_size` (`portrait_image_id` INTEGER NOT NULL, `width` INTEGER NOT NULL, `height` INTEGER NOT NULL, `url` TEXT NOT NULL, PRIMARY KEY(`portrait_image_id`, `width`), FOREIGN KEY(`portrait_image_id`) REFERENCES `portrait_image`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `similar_species` (`portrait_id` INTEGER NOT NULL, `similar_to_id` INTEGER NOT NULL, `differences` TEXT NOT NULL, PRIMARY KEY(`portrait_id`, `similar_to_id`), FOREIGN KEY(`portrait_id`) REFERENCES `portrait`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`similar_to_id`) REFERENCES `species`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `character` (`rowid` INTEGER NOT NULL, `gername` TEXT NOT NULL, `engname` TEXT NOT NULL, `group` TEXT NOT NULL, `weight` INTEGER NOT NULL, `single` INTEGER NOT NULL, `gerdescription` TEXT, `engdescription` TEXT, PRIMARY KEY(`rowid`));"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `character_value` (`rowid` INTEGER NOT NULL, `character_id` INTEGER NOT NULL, `gername` TEXT NOT NULL, `engname` TEXT NOT NULL, `has_image` INTEGER NOT NULL, PRIMARY KEY(`rowid`), FOREIGN KEY(`character_id`) REFERENCES `character`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `character_value_species` (`rowid` INTEGER NOT NULL, `character_value_id` INTEGER NOT NULL, `species_id` INTEGER NOT NULL, `weight` INTEGER NOT NULL, `female` INTEGER, PRIMARY KEY(`rowid`), FOREIGN KEY(`character_value_id`) REFERENCES `character_value`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`species_id`) REFERENCES `species`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `unambiguous_feature` (`portrait_id` INTEGER NOT NULL, `description` TEXT NOT NULL, PRIMARY KEY(`portrait_id`, `description`), FOREIGN KEY(`portrait_id`) REFERENCES `portrait`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `good_to_know` (`portrait_id` INTEGER NOT NULL, `fact` TEXT NOT NULL, PRIMARY KEY(`portrait_id`, `fact`), FOREIGN KEY(`portrait_id`) REFERENCES `portrait`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `sources_imprint` (`id` INTEGER NOT NULL, `scie_name` TEXT NOT NULL, `scie_name_eng` TEXT NOT NULL, `image_source` TEXT, `licence` TEXT, `author` TEXT, PRIMARY KEY(`id`));"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `sources_translations` (`language` INTEGER NOT NULL, `key` TEXT NOT NULL, `value` TEXT NOT NULL, PRIMARY KEY(`language`, `key`));"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `time_zone_polygon` (`rowid` INTEGER NOT NULL, `zone_id` TEXT NOT NULL, PRIMARY KEY(`rowid`));"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `time_zone_vertex` (`rowid` INTEGER NOT NULL, " +
        "`polygon_id` INTEGER NOT NULL, " +
        "`latitude` REAL NOT NULL, " +
        "`longitude` REAL NOT NULL, PRIMARY KEY(`rowid`), FOREIGN KEY(`polygon_id`) REFERENCES `time_zone_polygon`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
    )
    sqlite_cursor.execute(
        "CREATE TABLE IF NOT EXISTS `species_current_version` (`rowid` INTEGER NOT NULL," +
        "`version` INTEGER NOT NULL, PRIMARY KEY(`rowid`));"
    )
