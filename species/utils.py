import json
import logging
import sqlite3
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import requests

from species.models import Species, SpeciesName, SourcesTranslation, SourcesImprint, Faunaportrait, Floraportrait
from .utils_characters import insert_characters

logger = logging.getLogger(__name__)


@dataclass
class DbPortrait:
    rowid: int
    species_id: int
    language: int
    description: str
    in_the_city: str
    description_image_id: int = field(default=None)
    landscape: int = field(default=True)
    focus: float = field(default=50.0)
    in_the_city_image_id: int = field(default=None)
    good_to_know_image_id: int = field(default=None)
    sources: str = field(default=None)
    audio_url: str = field(default=None)


def insert_image_size(sqlite_cursor, img, portrait_image_id):
    if img:
        sqlite_cursor.execute("INSERT INTO portrait_image_size VALUES (?, ?, ? ,?)",
                              (portrait_image_id, img.width, img.height, img.url))


def insert_image(sqlite_cursor, meta, portrait_image_id):
    text = meta.text
    pif = meta.portrait_image_file
    sqlite_cursor.execute("INSERT INTO portrait_image VALUES (?, ?, ?, ?, ?, ?)",
                          (portrait_image_id, pif.owner, pif.owner_link, pif.source, text, pif.license))

    insert_image_size(sqlite_cursor, pif.image, portrait_image_id)
    insert_image_size(sqlite_cursor, pif.small, portrait_image_id)
    insert_image_size(sqlite_cursor, pif.medium, portrait_image_id)
    insert_image_size(sqlite_cursor, pif.large, portrait_image_id)


def lang_to_int(lang):
    match lang:
        case 'de':
            return 1
        case 'en':
            return 2
        case 'sf':
            return 3
        case 'dels':
            return 4
        case _:
            raise Exception("unknown language during db generation")


def get_focus(descmeta, ratio):
    if float(descmeta.portrait_image_file.width) / float(descmeta.portrait_image_file.height) > ratio:
        return descmeta.focus_point_horizontal if descmeta.focus_point_horizontal else 50.0
    else:
        return descmeta.focus_point_vertical if descmeta.focus_point_vertical else 50.0


def insert_portrait_image_and_sizes(sqlite_cursor, portraits):
    portrait_id = 1
    portrait_image_id = 1

    for p in portraits:
        db_portrait = DbPortrait(rowid=portrait_id,
                                 species_id=p.species.id,
                                 language=lang_to_int(p.language),
                                 description=p.db_description,
                                 in_the_city=p.db_in_the_city,
                                 sources=p.db_sources)

        if hasattr(p, 'faunaportrait_audio_file') and p.faunaportrait_audio_file:
            db_portrait.audio_url = p.faunaportrait_audio_file.audio_file.url

        if hasattr(p, 'descmeta'):
            insert_image(sqlite_cursor, p.descmeta, portrait_image_id)
            db_portrait.description_image_id = portrait_image_id
            db_portrait.landscape = 1 if p.descmeta.display_ratio == '4-3' else 0
            ratio = 4.0 / 3.0 if db_portrait.landscape == 1 else 3.0 / 4.0
            db_portrait.focus = get_focus(descmeta=p.descmeta, ratio=ratio)
            portrait_image_id += 1

        if hasattr(p, 'funfactmeta'):
            insert_image(sqlite_cursor, p.funfactmeta, portrait_image_id)
            db_portrait.good_to_know_image_id = portrait_image_id
            portrait_image_id += 1

        if hasattr(p, 'inthecitymeta'):
            insert_image(sqlite_cursor, p.inthecitymeta, portrait_image_id)
            db_portrait.in_the_city_image_id = portrait_image_id
            portrait_image_id += 1

        insert_portrait(sqlite_cursor, db_portrait)

        insert_similar_species(sqlite_cursor, portrait_id, p)
        insert_unambiguous_feature(sqlite_cursor, portrait_id, p)
        insert_good_to_know(sqlite_cursor, portrait_id, p)

        portrait_id += 1


def insert_portrait(sqlite_cursor, db_portrait):
    db_data = (db_portrait.rowid,
               db_portrait.species_id,
               allow_break_on_hyphen(db_portrait.description),
               db_portrait.description_image_id,
               db_portrait.language,
               allow_break_on_hyphen(db_portrait.in_the_city),
               db_portrait.in_the_city_image_id,
               db_portrait.good_to_know_image_id,
               allow_break_on_hyphen(db_portrait.sources),
               db_portrait.audio_url,
               db_portrait.landscape,
               db_portrait.focus
               )
    sqlite_cursor.execute("INSERT INTO portrait VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?)", db_data)


def insert_similar_species(sqlite_cursor, portrait_id, portrait):
    if hasattr(portrait, 'similarspecies_set'):
        data = list(map(lambda s: (portrait_id, s.species.id, allow_break_on_hyphen(s.differences)),
                        portrait.similarspecies_set.all()))
        sqlite_cursor.executemany("INSERT INTO similar_species VALUES (?, ?, ?);", data)


def insert_unambiguous_feature(sqlite_cursor, portrait_id, portrait):
    if hasattr(portrait, 'unambigousfeature_set'):
        data = list(map(lambda u: (portrait_id, u.description),
                        portrait.unambigousfeature_set.all()))
        sqlite_cursor.executemany("INSERT INTO unambiguous_feature VALUES (?, ?);", data)


def insert_good_to_know(sqlite_cursor, portrait_id, portrait):
    if hasattr(portrait, 'goodtoknow_set'):
        data = list(map(lambda gtk: (portrait_id, gtk.fact),
                        portrait.goodtoknow_set.all()))
        sqlite_cursor.executemany("INSERT INTO good_to_know VALUES (?, ?);", data)


def insert_sources_translations(sqlite_cursor):
    data = list(map(lambda st: (lang_to_int(st.language), f"{{{{{st.key}}}}}", st.value),
                    SourcesTranslation.objects.all()))
    sqlite_cursor.executemany("INSERT INTO sources_translations VALUES (?, ?, ?);", data)


def insert_sources_imprint(sqlite_cursor):
    data = list(map(lambda si: (
        si.id, si.scie_name, si.scie_name_eng if si.scie_name_eng else '', si.image_source, si.licence, si.author),
                    SourcesImprint.objects.all()))
    sqlite_cursor.executemany("INSERT INTO sources_imprint VALUES (?, ?, ?, ?, ?, ?);", data)


def insert_current_version(sqlite_cursor):
    url = "http://playback:9000/speciesdbversion"
    response = requests.get(url)
    if response.status_code == 200:
        sqlite_cursor.execute("INSERT INTO species_current_version VALUES (?, ?);", (1, response.json()["version"]))
    else:
        logger.error(f"Playback not available: response [ {response.text} ]")


def insert_timezone_polygon(sqlite_cursor):
    # Get the base directory of the project
    base_dir = Path(__file__).resolve().parent.parent
    json_path = base_dir / 'species' / 'data' / '2023b_simplify_0_05.json'
    from types import SimpleNamespace

    polygon_id = 1

    with open(json_path, encoding='utf-8') as j:
        polygons = json.load(j, object_hook=lambda d: SimpleNamespace(**d))
        for f in polygons.features:
            if f.geometry.type == 'Polygon':
                sqlite_cursor.execute("INSERT INTO time_zone_polygon VALUES (?, ?)", (polygon_id, f.properties.tzid))
                # First is boundary, all holes are ignored and therefore coordinates[0]
                for v in f.geometry.coordinates[0]:
                    sqlite_cursor.execute(
                        "INSERT INTO time_zone_vertex (polygon_id, longitude, latitude) VALUES (?, ?, ?)",
                        (polygon_id, v[0], v[1]))
                polygon_id += 1
            elif f.geometry.type == 'MultiPolygon':
                for c in f.geometry.coordinates:
                    sqlite_cursor.execute("INSERT INTO time_zone_polygon VALUES (?, ?)",
                                          (polygon_id, f.properties.tzid))
                    # First is boundary, all holes are ignored and therefore coordinates[0]
                    for v in c[0]:
                        sqlite_cursor.execute(
                            "INSERT INTO time_zone_vertex (polygon_id, longitude, latitude) VALUES (?, ?, ?)",
                            (polygon_id, v[0], v[1]))
                    polygon_id += 1


def create_sqlite_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    portraits = (list(Faunaportrait.objects.filter(published=True, language__in=['de','en']))
                 + list(Floraportrait.objects.filter(published=True, language__in=['de','en'])))

    insert_species(sqlite_cursor)
    insert_portrait_image_and_sizes(sqlite_cursor, portraits)
    insert_sources_translations(sqlite_cursor)
    insert_sources_imprint(sqlite_cursor)
    insert_current_version(sqlite_cursor)
    insert_timezone_polygon(sqlite_cursor)
    insert_characters(sqlite_cursor)

    sqlite_conn.commit()
    sqlite_conn.close()

    return temp_file.name


def get_synonnyms(language, species_id):
    synonyms = ", ".join(
        SpeciesName.objects.filter(species=species_id, language=language).order_by('name').values_list("name", flat=True))
    return allow_break_on_hyphen(synonyms) or None


def allow_break_on_hyphen(s):
    return s.replace("-", "\u200b-\u200b") if s else None


def insert_species(sqlite_cursor):
    data = list(map(map_species(), Species.objects.all()))
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
        allow_break_on_hyphen(s.engname),
        s.wikipedia,
        s.avatar.image.url if s.avatar else None,
        s.female_avatar.image.url if s.female_avatar else None,
        get_synonnyms('de', s.id),
        get_synonnyms('en', s.id), s.red_list_germany, s.iucncategory, s.speciesid, s.gbifusagekey,
        s.accepted_species.id if s.accepted_species else None,
        None,  # gersearchfield - per update later
        None)  # engsearchfield - per update later


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
