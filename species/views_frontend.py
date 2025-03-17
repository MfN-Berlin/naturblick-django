# /species/portrait?${idQuery}&lang=${lang.lang}
# /tags?${filterByTags.join('&')}&_limit=-1
# '/species';
#     this.speciesUrl + '?' + speciesids.map(id => `speciesid_in=${id}`).join('&'));
#     1
#
#
# /strapi/species/49
# /species/filter?lang=de&query=&_limit=3
# /species/portrait?id=160&lang=de
#
# /species-image-lists/filter?tag=138&lang=de&_sort=localname:ASC&_start=0&_limit=8
# /tags/filter?lang=de&tagsearch=&_limit=-1
# /uploads/thumbnail_crop_f0d08030b593c662206f5bd3_636e2b8a66.jpg






# /species/{id}
# expects `Species`    species/1
# export interface SpeciesName { name: string, language: number }
#
# export interface Species {
#   id: number;
#   speciesid: string,
#   group: string,
#   sciname: string,
#   gername: string,
#   engname: string,
#   speciesnames: SpeciesName[] }

# '/species?speciesid_in=herb_22222222&speciesid_in=herb_10f31f57...'
# expects `Species[]`  [{...}]