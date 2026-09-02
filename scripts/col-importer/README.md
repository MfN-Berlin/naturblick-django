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



