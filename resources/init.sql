# Prepare data in strapi-db
# docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits|floraportrait|components_species*' --schema-only strapi | sed s'/public\./strapi_/g' | sed '/^SET/d' | sed '/^SELECT pg_catalog\.set/d' | sed '/^--/d' | sed '/.*OWNED.*/d' | sed '/.*OWNER.*/d' | sed '/^ALTER TABLE ONLY.*regclass);/d' | sed '/^GRANT SELECT.*/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi_components_speciesportrait_species_portrait_images_components/strapi_components_speciesportrait_species_portrait_images_compo/g' | sed 's/species_pkey/strapi_species_pkey/g' | sed '/^$/d' > schema.sql
# docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits|floraportrait|components_species*' --column-inserts --data-only strapi | sed s'/public\./strapi_/g' | sed '/^SET/d' | sed '/^SELECT pg_catalog\.set/d' | sed '/^--/d' | sed '/.*OWNED.*/d' | sed '/.*OWNER.*/d' | sed '/^ALTER TABLE ONLY.*regclass);/d' | sed '/^GRANT SELECT.*/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi_components_speciesportrait_species_portrait_images_components/strapi_components_speciesportrait_species_portrait_images_compo/g' | sed 's/species_pkey/strapi_species_pkey/g' | sed '/^$/d' > data.sql
# docker exec django-db psql -U naturblick species -f /schema.sql
# docker exec django-db psql -U naturblick species -f /data.sql

insert into species (id,speciesid,gername,sciname,engname,wikipedia,nbclassid,red_list_germany,iucncategory ,activity_start_month ,activity_end_month, activity_start_hour, activity_end_hour, gbifusagekey, accepted, created_at, updated_at, group_id)
select s.id, s.speciesid, s.gername, s.sciname, s.engname, s.wikipedia, s.nbclassid, s."redListGermany", s.iucncategory, s."activityStartMonth", s."activityEndMonth", s."activityStartHour", s."activityEndHour", s.gbifusagekey, s.accepted, s.created_at, s.updated_at, g.id
from strapi_species as s
join "group" as g on s."group" = g.name;

delete from strapi_speciesnames where species is null;
delete from strapi_speciesnames where language is null;

insert into species_name (id, name, language, species_id)
select id, name, CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 3 THEN 'sf'
    WHEN language = 4 THEN 'er'
END, species
from strapi_speciesnames;

insert into portrait (language, short_description, city_habitat, human_interaction, published, species_id)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 3 THEN 'sf'
    WHEN language = 4 THEN 'er'
END, "shortDescription", "cityHabitat", "humanInteraction", preview, species
from strapi_floraportrait;

insert into flora_portrait (portrait_ptr_id, leaf_description, stem_axis_description, flower_description, fruit_description)
select p.id, "leafDescription", "stemAxisDescription", "flowerDescription", "fruitDescription"
from strapi_floraportrait as sf
join portrait as p on p.species_id = sf.species and p.language = CASE
    WHEN sf.language = 1 THEN 'de'
    WHEN sf.language = 2 THEN 'en'
    WHEN sf.language = 3 THEN 'sf'
    WHEN sf.language = 4 THEN 'er'
END;

delete from strapi_faunaportraits where species is null;
insert into portrait (language, short_description, city_habitat, human_interaction, published, species_id)
select CASE
    WHEN language = 1 THEN 'de'
    WHEN language = 2 THEN 'en'
    WHEN language = 3 THEN 'sf'
    WHEN language = 4 THEN 'er'
END, "shortDescription", "cityHabitat", "humanInteraction", preview, species
from strapi_faunaportraits;

# missing: audio_file, audio_spectrogram
insert into fauna_portrait (portrait_ptr_id, male_description, female_description, juvenile_description, tracks, audio_title, audio_license)
select p.id, sf."maleDescription", sf."femaleDescription", sf."juvenileDescription", sf.tracks, sf."audioTitle", sf."audioLicense"
from strapi_faunaportraits as sf
join portrait as p on p.species_id = sf.species and p.language = CASE
    WHEN sf.language = 1 THEN 'de'
    WHEN sf.language = 2 THEN 'en'
    WHEN sf.language = 3 THEN 'sf'
    WHEN sf.language = 4 THEN 'er'
END;
