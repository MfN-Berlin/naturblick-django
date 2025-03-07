import logging
import sqlite3
import tempfile
from dataclasses import dataclass

from species.models import Species, SpeciesName, Faunaportrait

#
#
#
#   INSERT ALL SPECIES !!
#
#
#
#

logger = logging.getLogger(__name__)


# CREATE TABLE `portrait` (`rowid` INTEGER NOT NULL, `species_id` INTEGER NOT NULL, `description` TEXT NOT NULL, `description_image_id` INTEGER, `language` INTEGER NOT NULL, `in_the_city` TEXT NOT NULL, `in_the_city_image_id` INTEGER, `good_to_know_image_id` INTEGER, `sources` TEXT, `audio_url` TEXT,
# `landscape` INTEGER NOT NULL, `focus` REAL NOT NULL,
# PRIMARY KEY(`rowid`), FOREIGN KEY(`species_id`) REFERENCES `species`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`description_image_id`) REFERENCES `portrait_image`(`rowid`) ON UPDATE NO ACTION ON DELETE SET NULL , FOREIGN KEY(`in_the_city_image_id`) REFERENCES `portrait_image`(`rowid`) ON UPDATE NO ACTION ON DELETE SET NULL , FOREIGN KEY(`good_to_know_image_id`) REFERENCES `portrait_image`(`rowid`) ON UPDATE NO ACTION ON DELETE SET NULL );


@dataclass
class DbPortrait():
    rowid: int
    species_id: int
    description: str
    description_image_id: int
    language: int
    in_the_city: str
    in_the_city_image_id: int
    good_to_know_image_id: int
    sources: str
    audio_url: str
    landscape: int
    focus: float


def insert_image_size(sqlite_cursor, img, next_id):
    if img:
        sqlite_cursor.execute("INSERT INTO portrait_image_size VALUES (?, ?, ? ,?)",
                              (next_id, img.width, img.height, img.url))


def insert_image(sqlite_cursor, meta, next_id):
    text = meta.text
    pif = meta.portrait_image_file
    sqlite_cursor.execute("INSERT INTO portrait_image VALUES (?, ?, ?, ?, ?, ?)",
                          (next_id, pif.owner, pif.owner_link, pif.source, text, pif.license))

    insert_image_size(sqlite_cursor, pif.small, next_id)
    insert_image_size(sqlite_cursor, pif.medium, next_id)
    insert_image_size(sqlite_cursor, pif.large, next_id)
    insert_image_size(sqlite_cursor, pif.thumbnail, next_id)


def lang_to_int(lang):
    match lang:
        case 'de':
            return 1
        case 'en':
            return 2
        case _:
            return 3


def get_focus(descmeta, ratio):
    if float(descmeta.portrait_image_file.width) / float(descmeta.portrait_image_file.height) > ratio:
        return descmeta.focus_point_horizontal if descmeta.focus_point_horizontal else 50.0
    else:
        return descmeta.focus_point_vertical if descmeta.focus_point_vertical else 50.0


def insert_portrait_image_and_sizes(sqlite_cursor, portraits, next_id):
    for p in portraits:

        if not hasattr(p, 'descmeta'):
            logger.error("every Portrait must have a description image!")
            continue

        # sources # sources.joinToString("\n\n")
        sources = allow_break_on_hyphen('foo')

        # audio_url
        audio_url = 'foo'
        landscape = 1 if p.descmeta.display_ratio == '4-3' else 0
        ratio = 4.0 / 3.0 if (landscape == 1) else 3.0 / 4.0
        focus = get_focus(descmeta=p.descmeta, ratio=ratio)

        db_portrait = DbPortrait(rowid=p.portrait_ptr_id, species_id=p.species.id, language=lang_to_int(
            p.language), description_image_id=next_id, description=allow_break_on_hyphen(p.description),
                                 sources=sources,
                                 audio_url=audio_url, focus=focus, landscape=landscape, in_the_city_image_id=0,
                                 in_the_city='', good_to_know_image_id=0)
        # todo johannes das ist alles ein wenig chaotisch

        insert_image(sqlite_cursor, p.descmeta, next_id)

        next_id += 1

        if hasattr(p, 'funfactmeta'):
            insert_image(sqlite_cursor, p.funfactmeta, next_id)
            db_portrait.good_to_know_image_id = next_id
            next_id += 1
        if hasattr(p, 'inthecitymeta'):
            insert_image(sqlite_cursor, p.inthecitymeta, next_id)
            db_portrait.in_the_city_image_id = next_id
            db_portrait.in_the_city = p.inthecitymeta.text
            next_id += 1
        insert_portrait(sqlite_cursor, db_portrait)


def insert_portrait(sqlite_cursor, portrait):
    data = (portrait.rowid,
            portrait.species_id,
            portrait.description,
            portrait.description_image_id,
            portrait.language,
            portrait.in_the_city,
            portrait.in_the_city_image_id,
            portrait.good_to_know_image_id,
            portrait.sources,
            portrait.audio_url,
            portrait.landscape,
            portrait.focus
            )
    sqlite_cursor.execute("INSERT INTO portrait VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?)", data)


def insert_similar_species(sqlite_cursor):
    # `portrait_id` INTEGER NOT NULL, `similar_to_id` INTEGER NOT NULL, `differences` TEXT NOT NULL
    # "INSERT INTO similar_species VALUES (?, ?, ?);"
    pass


def insert_unambiguous_feature(sqlite_cursor):
    # "INSERT INTO unambiguous_feature VALUES (?, ?);"
    pass


def insert_good_to_know(sqlite_cursor):
    # "INSERT INTO good_to_know VALUES (?, ?);"
    pass


def create_sqlite_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    insert_species(sqlite_cursor)

    next_id = 0
    faunaportraits = list(Faunaportrait.objects.all())
    next_id = insert_portrait_image_and_sizes(sqlite_cursor, faunaportraits, next_id)
    floraportraits = list(Faunaportrait.objects.all())
    insert_portrait_image_and_sizes(sqlite_cursor, floraportraits, next_id)

    insert_similar_species(sqlite_cursor)
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
