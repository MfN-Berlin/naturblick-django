insert into species (id,speciesid,gername,sciname,engname,wikipedia,nbclassid,red_list_germany,iucncategory ,activity_start_month ,activity_end_month, activity_start_hour, activity_end_hour, gbifusagekey, accepted_id, created_at, updated_at, group_id)
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
END, "shortDescription", "cityHabitat", "humanInteraction", published_at is not null, species
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
END, "shortDescription", "cityHabitat", "humanInteraction", published_at is not null, species
from strapi_faunaportraits;

-- missing: audio_file, audio_spectrogram
insert into fauna_portrait (portrait_ptr_id, male_description, female_description, juvenile_description, tracks, audio_title)
select p.id, sf."maleDescription", sf."femaleDescription", sf."juvenileDescription", sf.tracks, sf."audioTitle"
from strapi_faunaportraits as sf
join portrait as p on p.species_id = sf.species and p.language = CASE
    WHEN sf.language = 1 THEN 'de'
    WHEN sf.language = 2 THEN 'en'
    WHEN sf.language = 3 THEN 'sf'
    WHEN sf.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
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
    WHEN fp.language = 4 THEN 'er'
END
join strapi_components_speciesportrait_features as f on f.id = fpc.component_id
where fpc.component_type = 'components_speciesportrait_features';

-- portrait images description
insert into description_image_file (owner, owner_link, source, license, text, image, species_id)
select scp."imageOwner", scp."imageOwnerLink", scp."imageSource", scp."imageLicense", scp."imageText", 'portrait_images/' || substr(su.url, 10), p.species_id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'er' THEN 4
END
join strapi_species_image_lists_components as silc2
    on silc2.species_image_list_id = sil.id and silc2.component_type = 'components_speciesportrait_species_portrait_images' and silc2.field = 'description'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc2.component_id
join strapi_species_image_lists_components as silc
    on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures' and silc."order" = sci."imageFromList"
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_upload_file_morph as sm on sm.related_type = 'components_speciesportrait_species_pictures' and sm.related_id = scp.id
join strapi_upload_file as su on su.id = sm.upload_file_id;

-- there is a failure in the data, i delete the older one of the duplicates
delete from strapi_components_speciesportrait_species_portrait_images where id = 215;
insert into description_image_meta (image_orientation, display_ratio, grid_ratio, focus_point_vertical, focus_point_horizontal, portrait_id)
select sci."imageOrientation", sci."displayRatio", sci."gridRatio", sci."focusPointVertical", sci."focusPointHorizontal", p.id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'er' THEN 4
END
join strapi_species_image_lists_components as silc2
    on silc2.species_image_list_id = sil.id and silc2.component_type = 'components_speciesportrait_species_portrait_images' and silc2.field = 'description'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc2.component_id
join strapi_species_image_lists_components as silc
    on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures' and silc."order" = sci."imageFromList"
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_upload_file_morph as sm on sm.related_type = 'components_speciesportrait_species_pictures' and sm.related_id = scp.id
join strapi_upload_file as su on su.id = sm.upload_file_id;

-- portrait images fun_fact
insert into fun_fact_image_file (owner, owner_link, source, license, text, image, species_id)
select scp."imageOwner", scp."imageOwnerLink", scp."imageSource", scp."imageLicense", scp."imageText", 'portrait_images/' || substr(su.url, 10), p.species_id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'er' THEN 4
END
join strapi_species_image_lists_components as silc2 on silc2.species_image_list_id = sil.id and silc2.component_type = 'components_speciesportrait_species_portrait_images' and silc2.field = 'funFacts'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc2.component_id
join strapi_species_image_lists_components as silc on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures' and silc."order" = sci."imageFromList"
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_upload_file_morph as sm on sm.related_type = 'components_speciesportrait_species_pictures' and sm.related_id = scp.id
join strapi_upload_file as su on su.id = sm.upload_file_id;

-- there is a failure in the data, i delete the older entry
delete from strapi_components_speciesportrait_species_portrait_images where id = 217;
insert into fun_fact_image_meta (image_orientation, display_ratio, grid_ratio, focus_point_vertical, focus_point_horizontal, portrait_id)
select sci."imageOrientation", sci."displayRatio", sci."gridRatio", sci."focusPointVertical", sci."focusPointHorizontal", p.id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'er' THEN 4
END
join strapi_species_image_lists_components as silc on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_portrait_images' and silc.field = 'funFacts'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc.component_id;

-- portrait images in_the_city
insert into in_the_city_image_file (owner, owner_link, source, license, text, image, species_id)
select scp."imageOwner", scp."imageOwnerLink", scp."imageSource", scp."imageLicense", scp."imageText", 'portrait_images/' || substr(su.url, 10), p.species_id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'er' THEN 4
END
join strapi_species_image_lists_components as silc2 on silc2.species_image_list_id = sil.id and silc2.component_type = 'components_speciesportrait_species_portrait_images' and silc2.field = 'inTheCity'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc2.component_id
join strapi_species_image_lists_components as silc on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_pictures' and silc."order" = sci."imageFromList"
join strapi_components_speciesportrait_species_pictures as scp on scp.id = silc.component_id
join strapi_upload_file_morph as sm on sm.related_type = 'components_speciesportrait_species_pictures' and sm.related_id = scp.id
join strapi_upload_file as su on su.id = sm.upload_file_id;

insert into in_the_city_image_meta (image_orientation, display_ratio, grid_ratio, focus_point_vertical, focus_point_horizontal, portrait_id)
select distinct sci."imageOrientation", sci."displayRatio", sci."gridRatio", sci."focusPointVertical", sci."focusPointHorizontal", p.id
from strapi_species_image_lists as sil
join portrait as p on sil.species = p.species_id and sil.language = CASE
    WHEN p.language = 'de' THEN 1
    WHEN p.language = 'en' THEN 2
    WHEN p.language = 'sf' THEN 3
    WHEN p.language = 'er' THEN 4
END
join strapi_species_image_lists_components as silc on silc.species_image_list_id = sil.id and silc.component_type = 'components_speciesportrait_species_portrait_images' and silc.field = 'inTheCity'
join strapi_components_speciesportrait_species_portrait_images as sci on sci.id = silc.component_id;