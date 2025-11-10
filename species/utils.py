import json
import os
import re
import sqlite3
import tempfile
import uuid
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from image_cropping.utils import get_backend

from species.models import Species, SpeciesName, SourcesTranslation, SourcesImprint, Faunaportrait, Floraportrait, Group
from .utils_characters import insert_characters


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
        is_de = portrait.language == 'de'

        labels = {
            "blossom": "Blüte: " if is_de else "Blossom: ",
            "usage": "Nutzung: " if is_de else "Usage: ",
            "distribution": "Verbreitung: " if is_de else "Distribution: ",
            "lifeform": "Lebensform: " if is_de else "Lifeform: "
        }

        data = list(map(lambda gtk: (portrait_id, labels.get(gtk.type, "") + gtk.fact),
                        portrait.goodtoknow_set.all()))
        sqlite_cursor.executemany("INSERT INTO good_to_know VALUES (?, ?);", data)


def insert_sources_translations(sqlite_cursor):
    data = list(map(lambda st: (lang_to_int(st.language), f"{{{{{st.key}}}}}", st.value),
                    SourcesTranslation.objects.all()))
    sqlite_cursor.executemany("INSERT INTO sources_translations VALUES (?, ?, ?);", data)


def insert_sources_imprint(sqlite_cursor):
    data = list(map(lambda si: (
        si.id, si.name, si.scie_name, si.scie_name_eng if si.scie_name_eng else '', si.image_source, si.licence,
        si.author),
                    SourcesImprint.objects.all()))
    sqlite_cursor.executemany("INSERT INTO sources_imprint VALUES (?, ?, ?, ?, ?, ?, ?);", data)


def insert_current_version(sqlite_cursor):
    if os.environ.get('DJANGO_ENV') == 'development':
        return "1"
    url = "http://playback:9000/speciesdbversion"
    response = requests.get(url)
    if response.status_code == 200:
        sqlite_cursor.execute("INSERT INTO species_current_version VALUES (?, ?);", (1, response.json()["version"]))
    else:
        raise Exception(f"Playback not available: response [ {response.text} ]")


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


def insert_groups(sqlite_cursor):
    data = list(
        map(lambda g: (g.name, g.nature, g.gername, g.engname, g.has_portraits, g.is_fieldbookfilter, g.has_characters),
            Group.objects.all()))
    sqlite_cursor.executemany("INSERT INTO groups VALUES (?, ?, ?, ?, ?, ?, ?);", data)


def create_sqlite_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    temp_file.close()

    sqlite_conn = sqlite3.connect(temp_file.name, autocommit=False)
    sqlite_cursor = sqlite_conn.cursor()

    create_tables(sqlite_cursor)

    portraits = (list(Faunaportrait.objects.filter(published=True, language__in=['de', 'en']))
                 + list(Floraportrait.objects.filter(published=True, language__in=['de', 'en'])))

    insert_groups(sqlite_cursor)
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


def get_synonyms(all_synonyms, language, species_id):
    synonyms = ", ".join(
        (s.name for s in all_synonyms if s.species_id == species_id and s.language == language))
    return allow_break_on_hyphen(synonyms) or None


def allow_break_on_hyphen(s):
    return s.replace("-", "\u200b-\u200b") if s else None


def insert_species(sqlite_cursor):
    all_synonyms = list(SpeciesName.objects.order_by('name').all())
    data = list(map(map_species(all_synonyms), Species.objects.select_related("group", "avatar_new", "female_avatar_new").all()))
    sqlite_cursor.executemany(
        "INSERT INTO species VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", data)

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
    sqlite_cursor.execute("ALTER TABLE species DROP COLUMN gbifusagekey;")


def cropped_image(image, cropping, size = (400,400)):
    return get_backend().get_thumbnail_url(
        image,
        {
            'size': size,
            'box': cropping,
            'crop': True,
            'detail': True,
        }
    )


def map_species(all_synonyms):
    return lambda s: (
        s.id, s.group.name, allow_break_on_hyphen(s.sciname), allow_break_on_hyphen(s.gername),
        allow_break_on_hyphen(s.engname),
        s.wikipedia,
        cropped_image(s.avatar_new.imagefile.image, s.avatar_new.cropping) if s.avatar_new else None,
        s.avatar_new.imagefile.image.url if s.avatar_new else None,
        s.avatar_new.imagefile.owner if s.avatar_new else None,
        s.avatar_new.imagefile.owner_link if s.avatar_new else None,
        s.avatar_new.imagefile.source if s.avatar_new else None,
        s.avatar_new.imagefile.license if s.avatar_new else None,
        cropped_image(s.female_avatar_new.imagefile.image, s.female_avatar_new.cropping) if s.female_avatar_new else None,
        get_synonyms(all_synonyms, 'de', s.id),
        get_synonyms(all_synonyms, 'en', s.id), s.red_list_germany, s.iucncategory, s.speciesid, s.gbifusagekey,
        s.accepted_species_id,
        None,  # gersearchfield - per update later
        None)  # engsearchfield - per update later


def create_tables(sqlite_cursor):
    sqlite_cursor.execute(
        "CREATE TABLE `groups` (`name` TEXT NOT NULL, `nature` TEXT, `gername` TEXT, `engname` TEXT, `has_portraits` INTEGER NOT NULL, `is_fieldbookfilter` INTEGER NOT NULL, `has_characters` INTEGER NOT NULL, PRIMARY KEY(`name`));"
    )
    sqlite_cursor.execute(
        "CREATE TABLE `species` (`rowid` INTEGER NOT NULL, `group_id` TEXT NOT NULL, `sciname` TEXT NOT NULL, `gername` TEXT, `engname` TEXT, `wikipedia` TEXT, `image_url` TEXT, `image_url_orig` TEXT, `image_url_owner` TEXT, `image_url_owner_link` TEXT, `image_url_source` TEXT, `image_url_license` TEXT, `female_image_url` TEXT, `gersynonym` TEXT, `engsynonym` TEXT, `red_list_germany` TEXT, `iucn_category` TEXT, `old_species_id` TEXT NOT NULL, `gbifusagekey` INTEGER, `accepted` INTEGER, `gersearchfield` TEXT, `engsearchfield` TEXT, PRIMARY KEY(`rowid`), FOREIGN KEY(`group_id`) REFERENCES `groups`(`name`));"
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
        "CREATE TABLE `sources_imprint` (`id` INTEGER NOT NULL, `section` TEXT NOT NULL, `scie_name` TEXT NOT NULL, `scie_name_eng` TEXT NOT NULL, `image_source` TEXT, `licence` TEXT, `author` TEXT, PRIMARY KEY(`id`));"
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


class ArtistLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.is_a = False
        self.has_a = False
        self.got_author = False
        self.got_href = False
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            if not self.got_href:
                self.href = [attr[1] for attr in attrs if attr[0] == 'href'][0]
                if self.href.startswith("//"):
                    self.href = "https:" + self.href
                self.got_href = True
            self.is_a = True
            self.has_a = True

    def handle_endtag(self, tag):
        self.is_a = False

    def handle_data(self, data):
        self.last_data = data
        if self.is_a and not self.got_author:
            self.author_data = data
            self.got_author = True

    @property
    def author(self):
        if self.has_a:
            return self.author_data
        else:
            return self.last_data


@dataclass
class ImageMetadata:
    license: str
    author: str
    author_url: str
    image_url: str
    image: ContentFile


def get_metadata(url):
    user_agent = 'Naturblick-Django (https://naturblick.museumfuernaturkunde.berlin/; naturblick@mfn.berlin)'
    path = urlparse(url).path
    wiki_file = path[path.index("File"):]
    image_filename = str(uuid.uuid4()) + wiki_file[wiki_file.index("."):].lower()
    response = requests.get(
        f"https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&format=json&iiprop=extmetadata&iilimit=1&titles={wiki_file}",
        headers={'User-Agent': user_agent})
    response.raise_for_status()
    metadata = list(response.json()['query']['pages'].values())[0]['imageinfo'][0]['extmetadata']
    raw_license = metadata['License']['value']
    license_version = re.search(r"\d.\d", metadata['License']['value'])
    if raw_license.startswith("cc") and license_version:
        license = (raw_license[:license_version.start() - 1].replace("-", " ", 1) + raw_license[
                                                                                    license_version.start() - 1:].replace(
            "-", " ")).upper()
    else:
        license = raw_license.replace("-", " ", 1).upper()
    parser = ArtistLinkParser()
    parser.feed(metadata['Artist']['value'])

    file_meta_response = requests.get(
        f"https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&format=json&iiprop=url&iilimit=1&titles={wiki_file}",
        headers={'User-Agent': user_agent})
    file_meta_response.raise_for_status()

    file_url = list(file_meta_response.json()['query']['pages'].values())[0]['imageinfo'][0]['url']

    file_response = requests.get(file_url, headers={
        'User-Agent': user_agent})
    file_response.raise_for_status()

    return ImageMetadata(license, parser.author, parser.href, url,
                         ContentFile(file_response.content, name=image_filename))
