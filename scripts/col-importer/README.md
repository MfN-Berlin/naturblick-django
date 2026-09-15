# Import taxons to complete taxonomy

This scripts imports all missing taxons from Catalogue of Life (CoL)
to complete a taxonomy. This means all missing parents and accepted
taxons are imported.

## Input format
The input is tab separated data containing our `species.id`,
`species.colid` and `species.sciname`, e.g.
```
\copy (select id, colid, sciname from species where colid is not null) TO '/tmp/species-with-colid.tsv';
```

## Output columns

### colid
CoL `id`, always set.

### name
CoL `scientificName` after a set of transformations as defined in the
script. Always set.

### rank
CoL `rank`. Only ranks either from a taxon in the input or in
ACCEPTED_RANKS. Always set.

### status
CoL `status`. For taxons not present in input the rank is always
`accepted` or `provisionally accepted`. Always set.

### parent
CoL `parentId`. The closest parent with a rank in ACCEPTED_RANKS is
used. Only set for accepted Taxons that are not the root taxon.

### accepted
CoL `accepted.id`. If the accepted taxon is of a rank not in
ACCEPTED_RANKS the closest parent (as described for parent above) is
used. Only set for taxons that are synonyms or of non accepted rank.

### species_id
Our `species.id`. Only set for taxons that were also present in input.


## Import querries

```sql
create table import_col (colid text not null,  name text not null, rank text not null, status text not null, parent text, accepted text, species_id integer references species (id));

\copy import_col from '/tmp/col-all-taxons.tsv' null '';

insert into col_species (colid, sciname, rank, status, species_id) (select colid, name, rank, status, species_id from import_col);


-- Set parents and accepted
update col_species s set parent_id = (select id from col_species where colid = i.parent), accepted_id = (select id from col_species where colid = i.accepted) from import_col i where s.colid = i.colid;

-- Set group from existing species
update col_species c set group_id = s.group_id from species s where s.id = c.species_id;

-- Set group for species and subspecies from synonym
update col_species a set group_id = s.group_id from col_species s where s.accepted_id = a.id and a.rank in ('species', 'subspecies') and a.group_id is null;

-- Set group for species and subspecies from children
update col_species a set group_id = s.group_id from col_species s where s.parent_id = a.id and a.rank in ('species', 'subspecies') and a.group_id is null;

-- Set group for genus from children, where all children have identical group
update col_species s1 set group_id = c1.group_id from col_species c1 where c1.parent_id = s1.id and s1.colid in (select s.colid from col_species s join col_species c on c.parent_id = s.id where s.rank = 'genus' and s.group_id is null group by s.colid having count(distinct c.group_id) = 1);

-- Set group for genus from synonyms where all synonyms have identical group
update col_species s1 set group_id = c1.group_id from col_species c1 where c1.accepted_id = s1.id and s1.colid in (select s.colid from col_species s join col_species c on c.accepted_id = s.id where s.rank = 'genus' and s.group_id is null group by s.colid having count(distinct c.group_id) = 1);

-- Genus whose children have different groups get special treatment
update col_species set group_id = 53 where colid = 'MJLPN';
update col_species set group_id = 30 where colid = '3SPG';
update col_species set group_id = 30 where colid = '8VRR8';
update col_species set group_id = 30 where colid = '8VRRF';
update col_species set group_id = 30 where colid = 'KV933';
update col_species set group_id = 30 where colid = 'N27JR';
```
