-- helpers

create view strapi_file as
select m.related_id, m.related_type, substr(f.url , 10) as url, m.field, f.width, f.height
from strapi_upload_file_morph as m
join strapi_upload_file as f on f.id = m.upload_file_id;

alter table avatar add column strapi_species varchar not null;

-- avatar
DELETE FROM strapi_species_avatars AS a USING (
    SELECT MIN(id) as id, species
    FROM strapi_species_avatars
    GROUP BY species HAVING COUNT(*) > 1
) AS b
WHERE a.species = b.species
AND a.id <> b.id;

insert into avatar (image, owner, owner_link, source, license, cropping, strapi_species)
select 'avatar_images/' || f.url,  scsp."imageOwner", scsp."imageOwnerLink", scsp."imageSource", scsp."imageLicense", '0,0,400,400', s.speciesid
from strapi_species_avatars as ssa
join strapi_species as s on s.id = ssa.species
join strapi_species_avatars_components as ssac on ssac.species_avatar_id = ssa.id and ssac.component_type = 'components_speciesportrait_species_pictures'
join strapi_components_speciesportrait_species_pictures as scsp on scsp.id = ssac.component_id
join strapi_file as f on f.related_type = 'components_speciesportrait_species_pictures' and f.related_id = ssac.component_id
where ssa.published_at is not null;

insert into species (id, speciesid, gername, sciname, engname, nbclassid, wikipedia, autoid, red_list_germany, iucncategory ,activity_start_month ,activity_end_month, activity_start_hour, activity_end_hour, gbifusagekey, accepted_species_id, created_at, updated_at, avatar_id, group_id, plantnetpowoid)
select s.id, s.speciesid, s.gername, s.sciname, s.engname, s.nbclassid, s.wikipedia, s.autoid, s."redListGermany", s.iucncategory, s."activityStartMonth", s."activityEndMonth", s."activityStartHour", s."activityEndHour", s.gbifusagekey, s.accepted, s.created_at, s.updated_at, a.id, g.id, s.plantnetpowoid
from strapi_species as s
join "group" as g on s."group" = g.name
left join avatar as a on a.strapi_species = s.speciesid and a.id not in (select female_avatar_id from species);

-- female avatar
with rows as (
    insert into avatar (image, owner, owner_link, source, license, cropping, strapi_species)
    select 'avatar_images/' || f.url,  a."imageOwner", a."imageOwnerLink", a."imageSource", a."imageLicense", '0,0,400,400', s.speciesid
    from strapi_species_components as sc
    join strapi_species as s on s.id = sc.species_id
    join strapi_components_speciesportrait_species_avatars as a on a.id = sc.component_id
    join strapi_file as f on f.related_id = a.id and f.related_type = 'components_speciesportrait_species_avatars'
    where sc.component_type = 'components_speciesportrait_species_avatars'
    returning *
)
update species set female_avatar_id = rows.id
from rows
where species.speciesid = rows.strapi_species;

-- drop helper column
alter table avatar drop column strapi_species;

delete from strapi_speciesnames where species is null;
delete from strapi_speciesnames where language is null;

insert into species_name (id, name, language, species_id)
select id, name, CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 3 THEN 'sf'
    WHEN language = 4 THEN 'dels'
END, species
from strapi_speciesnames
on conflict do nothing;

select setval('species_name_id_seq', (select max(id) from species_name));

insert into species_name (name, language, species_id)
select gernamesynonym, 'de', id
from strapi_species
where gernamesynonym is not null
on conflict do nothing;

insert into species_name (name, language, species_id)
select scinamesynonym, 'sf', id
from strapi_species
where scinamesynonym is not null
on conflict do nothing;

insert into portrait (language, short_description, city_habitat, human_interaction, published, species_id)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 3 THEN 'sf'
    WHEN language = 4 THEN 'dels'
END, "shortDescription", "cityHabitat", "humanInteraction", published_at is not null, species
from strapi_floraportrait;

insert into floraportrait (portrait_ptr_id, leaf_description, stem_axis_description, flower_description, fruit_description)
select p.id, "leafDescription", "stemAxisDescription", "flowerDescription", "fruitDescription"
from strapi_floraportrait as sf
join portrait as p on p.species_id = sf.species and p.language = CASE
    WHEN sf.language = 1 THEN 'de'
    WHEN sf.language = 2 THEN 'en'
    WHEN sf.language = 3 THEN 'sf'
    WHEN sf.language = 4 THEN 'dels'
END;

delete from strapi_faunaportraits where species is null;
insert into portrait (language, short_description, city_habitat, human_interaction, published, species_id)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 3 THEN 'sf'
    WHEN language = 4 THEN 'dels'
END, "shortDescription", "cityHabitat", "humanInteraction", published_at is not null, species
from strapi_faunaportraits;

-- missing: audio_file, audio_spectrogram
insert into faunaportrait (portrait_ptr_id, male_description, female_description, juvenile_description, tracks, audio_title)
select p.id, sf."maleDescription", sf."femaleDescription", sf."juvenileDescription", sf.tracks, sf."audioTitle"
from strapi_faunaportraits as sf
join portrait as p on p.species_id = sf.species and p.language = CASE
    WHEN sf.language = 1 THEN 'de'
    WHEN sf.language = 2 THEN 'en'
    WHEN sf.language = 3 THEN 'sf'
    WHEN sf.language = 4 THEN 'dels'
END;

-- fauna good_to_know
insert into good_to_know (fact, type, "order", portrait_id)
select gtk.fact, gtk.type, fpc."order", p.id
from strapi_faunaportraits as fp
join strapi_faunaportraits_components as fpc on fp.id = fpc.faunaportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_goodtoknows as gtk on gtk.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_goodtoknows';

-- flora good_to_know
insert into good_to_know (fact, type, "order", portrait_id)
select gtk.fact, gtk.type, fpc."order", p.id
from strapi_floraportrait as fp
join strapi_floraportrait_components as fpc on fp.id = fpc.floraportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_goodtoknows as gtk on gtk.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_goodtoknows';


-- fauna additional_link
insert into additional_link (title, description, url, "order", portrait_id)
select l.titel, l.description, l.url, fpc."order", p.id
from strapi_faunaportraits as fp
join strapi_faunaportraits_components as fpc on fp.id = fpc.faunaportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_links as l on l.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_links';

-- flora additional_link
insert into additional_link (title, description, url, "order", portrait_id)
select l.titel, l.description, l.url, fpc."order", p.id
from strapi_floraportrait as fp
join strapi_floraportrait_components as fpc on fp.id = fpc.floraportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_links as l on l.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_links';

-- fauna sources
insert into source (text, "order", portrait_id)
select s.source, fpc."order", p.id
from strapi_faunaportraits as fp
join strapi_faunaportraits_components as fpc on fp.id = fpc.faunaportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_sources as s on s.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_sources';

-- flora sources
insert into source (text, "order", portrait_id)
select s.source, fpc."order", p.id
from strapi_floraportrait as fp
join strapi_floraportrait_components as fpc on fp.id = fpc.floraportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_sources as s on s.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_sources';

-- clean strapi similar species
delete from strapi_components_speciesportrait_similar_species where specie is null;

-- fauna similar_species
insert into similar_species (differences, "order", portrait_id, species_id)
select s.differences, fpc."order", p.id, s.specie
from strapi_faunaportraits as fp
join strapi_faunaportraits_components as fpc on fp.id = fpc.faunaportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_similar_species as s on s.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_similar_species';

-- flora similar_species
insert into similar_species (differences, "order", portrait_id, species_id)
select s.differences, fpc."order", p.id, s.specie
from strapi_floraportrait as fp
join strapi_floraportrait_components as fpc on fp.id = fpc.floraportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_similar_species as s on s.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_similar_species';

-- fauna features
insert into unambigous_feature (description, "order", portrait_id)
select f.description, fpc."order", p.id
from strapi_faunaportraits as fp
join strapi_faunaportraits_components as fpc on fp.id = fpc.faunaportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_features as f on f.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_features';

-- flora features
insert into unambigous_feature (description, "order", portrait_id)
select f.description, fpc."order", p.id
from strapi_floraportrait as fp
join strapi_floraportrait_components as fpc on fp.id = fpc.floraportrait_id
join portrait as p on p.species_id = fp.species and p.language = CASE
    WHEN fp.language = 1 THEN 'de'
    WHEN fp.language = 2 THEN 'en'
    WHEN fp.language = 3 THEN 'sf'
    WHEN fp.language = 4 THEN 'dels'
END
join strapi_components_speciesportrait_features as f on f.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_features';

-- portrait images
insert into portrait_image_file (owner, owner_link, source, license, image, species_id, width, height)
select distinct scp."imageOwner", scp."imageOwnerLink", scp."imageSource", scp."imageLicense", 'portrait_images/' || f.url, sil.species, f.width, f.height
from strapi_species_image_lists as sil
join strapi_species_image_lists_components as silc
    on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures'
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_file as f on f.related_type = 'components_speciesportrait_species_pictures' and f.related_id = scp.id
where sil.published_at is not null;

-- delete double entries for the same image-url.
DELETE FROM portrait_image_file AS a USING (
    SELECT MIN(id) as id, image
    FROM portrait_image_file
    GROUP BY image HAVING COUNT(*) > 1
) AS b
WHERE a.image = b.image
AND a.id <> b.id;

--  DESC
insert into desc_meta (image_orientation, display_ratio, grid_ratio, focus_point_vertical, focus_point_horizontal, text, portrait_id, portrait_image_file_id)
select sci."imageOrientation", sci."displayRatio", sci."gridRatio", sci."focusPointVertical", sci."focusPointHorizontal", scp."imageText", p.id, pif.id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'dels' THEN 4
END
join strapi_species_image_lists_components as silc2
    on silc2.species_image_list_id = sil.id and silc2.component_type = 'components_speciesportrait_species_portrait_images' and silc2.field = 'description'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc2.component_id
join strapi_species_image_lists_components as silc
    on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures' and silc."order" = sci."imageFromList"
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_file as f on f.related_type = 'components_speciesportrait_species_pictures' and f.related_id = scp.id
join portrait_image_file as pif on pif.species_id = sil.species and 'portrait_images/' || f.url = pif.image
where sil.published_at is not null;

--  FUN_FACT
insert into funfact_meta (image_orientation, display_ratio, grid_ratio, focus_point_vertical, focus_point_horizontal, text, portrait_id, portrait_image_file_id)
select sci."imageOrientation", sci."displayRatio", sci."gridRatio", sci."focusPointVertical", sci."focusPointHorizontal", scp."imageText", p.id, pif.id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'dels' THEN 4
END
join strapi_species_image_lists_components as silc2
    on silc2.species_image_list_id = sil.id and silc2.component_type = 'components_speciesportrait_species_portrait_images' and silc2.field = 'funFacts'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc2.component_id
join strapi_species_image_lists_components as silc
    on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures' and silc."order" = sci."imageFromList"
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_file as f on f.related_type = 'components_speciesportrait_species_pictures' and f.related_id = scp.id
join portrait_image_file as pif on pif.species_id = sil.species and 'portrait_images/' || f.url = pif.image
where sil.published_at is not null;


-- IN THE CITY
insert into inthecity_meta (image_orientation, display_ratio, grid_ratio, focus_point_vertical, focus_point_horizontal, text, portrait_id, portrait_image_file_id)
select sci."imageOrientation", sci."displayRatio", sci."gridRatio", sci."focusPointVertical", sci."focusPointHorizontal", scp."imageText", p.id, pif.id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'dels' THEN 4
END
join strapi_species_image_lists_components as silc2
    on silc2.species_image_list_id = sil.id and silc2.component_type = 'components_speciesportrait_species_portrait_images' and silc2.field = 'inTheCity'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc2.component_id
join strapi_species_image_lists_components as silc
    on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures' and silc."order" = sci."imageFromList"
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_file as f on f.related_type = 'components_speciesportrait_species_pictures' and f.related_id = scp.id
join portrait_image_file as pif on pif.species_id = sil.species and 'portrait_images/' || f.url = pif.image
where sil.published_at is not null;

insert into character (id, gername, engname, display_name, weight, single_choice, gerdescription, engdescription, group_id)
select c.id, c.gername, c.engname, c."displayName", c.weight, c."singleChoice", c.gerdescription, c.engdescription, g.id
from strapi_characters as c
join "group" as g on g.name = c."group";

insert into character_value (id, gername, engname, colors, dots, image, character_id)
select v.id, v.gername, v.engname, v.colors, v.dots, 'character_images/' || f.url, v.character
from strapi_character_values as v
left join strapi_file f on f.related_id = v.id and f.related_type = 'character_values';

insert into tag (id, name, english_name)
select t.id, t.name, t."englishName"
from strapi_tags as t;

insert into species_tag (species_id, tag_id)
select st.species_id, st.tag_id
from strapi_species__tags as st
where exists (select * from tag where id = st.tag_id);

insert into sources_imprint (id, name, scie_name, scie_name_eng, image_source, image_link, licence, author)
select i.id, CASE
    WHEN i.name = 'Lauterkennung Bilder' THEN 'sound_recogniotion_images'
    WHEN i.name = 'Lauterkennung Tonaufnahmen' THEN 'sound_recogniotion_sounds'
    WHEN i.name = 'Bestimmungsschlüssel' THEN 'ident_keys'
END, i.scie_name, i.scie_name_eng, i.image_source, i.image_link, i.licence, i.author
from strapi_sources_impressum as i;


insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'page', page
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'wiki', wiki
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'revision', revision
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'accessed', accessed
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'version', version
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'volume', volume
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'editors', editors
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'nodate', nodate
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'in', "in"
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'published', published
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'edition', edition
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'part', part
from strapi_sources_translations;

insert into sources_translation (language, key, value)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 4 THEN 'dels'
END, 'changedby', changedby
from strapi_sources_translations;

with rows as (
    insert into faunaportrait_audio_file (owner, owner_link, source, license, audio_file, audio_spectrogram, species_id)
    select distinct 'todo', null, 'todo', COALESCE(sf."audioLicense", 'todo'),
        case
            when f1.url is not null then 'audio_files/' || f1.url
            else null
        end,
        case
            when f2.url is not null then 'spectrogram_images/' || f2.url
            else null
        end,
        sf.species
    from strapi_faunaportraits as sf
    left join strapi_file as f1 on f1.related_id = sf.id and f1.field = 'audioFile'
    left join strapi_file as f2 on f2.related_id = sf.id and f2.field = 'audioSpectrogram'
    where f1.url is not null or f2.url is not null returning *
)
update faunaportrait set faunaportrait_audio_file_id = r.id
from portrait as p, rows as r
where p.id = portrait_ptr_id
    and p.species_id = r.species_id;

drop view if exists strapi_file;

select setval('additional_link_id_seq', (select max(id) from additional_link));
select setval('avatar_id_seq', (select max(id) from avatar));
select setval('character_id_seq', (select max(id) from character));
select setval('character_value_id_seq', (select max(id) from character_value));
select setval('desc_meta_id_seq', (select max(id) from desc_meta));
select setval('faunaportrait_audio_file_id_seq', (select max(id) from faunaportrait_audio_file));
select setval('funfact_meta_id_seq', (select max(id) from funfact_meta));
select setval('good_to_know_id_seq', (select max(id) from good_to_know));
select setval('group_id_seq', (select max(id) from "group"));
select setval('inthecity_meta_id_seq', (select max(id) from inthecity_meta));
select setval('portrait_id_seq', (select max(id) from portrait));
select setval('portrait_image_file_id_seq', (select max(id) from portrait_image_file));
select setval('similar_species_id_seq', (select max(id) from similar_species));
select setval('source_id_seq', (select max(id) from source));
select setval('sources_imprint_id_seq', (select max(id) from sources_imprint));
select setval('sources_translation_id_seq', (select max(id) from sources_translation));
select setval('species_id_seq', (select max(id) from species));
select setval('species_name_id_seq', (select max(id) from species_name));
select setval('species_tag_id_seq', (select max(id) from species_tag));
select setval('tag_id_seq', (select max(id) from tag));
select setval('unambigous_feature_id_seq', (select max(id) from unambigous_feature));