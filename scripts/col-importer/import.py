import csv
import dataclasses
from itertools import groupby
import re
import sys
from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin

COL_URL = "https://api.checklistbank.org/dataset/315834/nameusage/{colid}"
USER_AGENT = 'Naturblick (https://naturblick.museumfuernaturkunde.berlin/; naturblick@mfn.berlin)'

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    """Session class with caching and rate-limiting behavior.
    Accepts keyword arguments for both LimiterSession and CachedSession.
    Mixin order (cache first, then limiter) assures that cache is not limited.
    """

session = CachedLimiterSession(cache_name='col_cache',per_second=5)
session.headers.update({'User-Agent': USER_AGENT})

@dataclasses.dataclass(frozen=True)
class Taxon:
    colid: str
    name: str
    rank: str
    status: str
    parent: str
    accepted: str
    species_id: int

    def as_row(self):
        return [self.colid, self.name, self.rank, self.status, self.parent, self.accepted, self.species_id]

def request_taxon(colid):
    response = session.get(COL_URL.format(colid=colid))
    response.raise_for_status()
    return response.json()

MATCH_COL_PAREN = re.compile(" [(](.*)[)]")

def clean_name(name, rank):
    cleaned_name = re.sub(MATCH_COL_PAREN, "", name).replace(' x ', ' × ')
    if rank != 'subspecies' or 'subsp.' in cleaned_name:
        return cleaned_name
    else:
        name_items = cleaned_name.split(' ')
        if len(name_items) != 3:
            raise ValueError(f"Subspecies: {name} can not be extended with subsp.")
        name_items.insert(2, "subsp.")

        return ' '.join(name_items)

def create_taxon_from_json(json, species_id):
    acceptedId = json["accepted"]["id"] if "accepted" in json else None
    # Not accepted species always have the accepted species as parent, we use None instead
    parent = json.get("parentId", None) if acceptedId == None else None
    rank = json["name"]["rank"]
    name = clean_name(json["name"]["scientificName"], rank)
    return Taxon(json["id"], name, rank, json["status"], parent, acceptedId, species_id)

def get_taxon(colid, species_id, taxons):
    if not colid in taxons or species_id != None:
        taxons[colid] = create_taxon_from_json(request_taxon(colid), species_id)
    return taxons[colid]

def get_taxon_hierarchy(colid, species_id, taxons):
    taxon = get_taxon(colid, species_id, taxons)
    if taxon.accepted != None:
        get_taxon_hierarchy(taxon.accepted, None, taxons)
    elif taxon.parent != None:
        get_taxon_hierarchy(taxon.parent, None, taxons)
    return taxon

def read_taxon_tsv(filename):
    with open(filename) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            yield row

ACCEPTED_RANKS = set(['domain', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'subspecies'])

def find_next_parent(taxon, taxons):
    if taxon.parent != None:
        parent = taxons[taxon.parent]
        if parent.rank not in ACCEPTED_RANKS:
            return find_next_parent(parent, taxons)
        else:
            return parent.colid
    else:
        return None

def find_next_accepted(taxon, taxons):
    if taxon.accepted != None:
        accepted = taxons[taxon.accepted]
        if accepted.rank not in ACCEPTED_RANKS:
            return find_next_parent(accepted, taxons)
        else:
            return accepted.colid
    else:
        return None

def prune_taxons(taxons):
    # Set all parents and accepted to allowed ranks and remove all not allowed ranks
    return { colid: dataclasses.replace(taxon, parent = find_next_parent(taxon, taxons), accepted = find_next_accepted(taxon, taxons)) for colid, taxon in taxons.items() if taxon.rank in ACCEPTED_RANKS or taxon.species_id != None }

def merge_taxon(taxon, synonyms):
    if taxon.colid in synonyms and taxon.species_id == None:
        return dataclasses.replace(taxon, species_id = synonyms[taxon.colid].species_id)
    else:
        return taxon

def print_deleted(taxons):
    for accepted_id, synonym in taxons.items():
        print(f"{synonym.name} ({synonym.colid}, {synonym.species_id}, parent: {synonym.parent}, accepted: {synonym.accepted}) replaced by {accepted_id}")

def find_matching_parent(rank, name, taxon, taxons):
    if taxon.rank == rank and taxon.name == name:
        return taxon.colid
    elif taxon.parent != None:
        return find_matching_parent(rank, name, taxons[taxon.parent], taxons)
    else:
        return None

def delete_false_synonyms(taxons):
    false_synonyms = dict()
    to_delete = list()
    for colid, taxon in taxons.items():
        if taxon.accepted != None:
            accepted = taxons[taxon.accepted]
            matching_id = find_matching_parent(taxon.rank, taxon.name, accepted, taxons)
            if matching_id != None:
                false_synonyms[matching_id] = taxon
                to_delete.append(taxon.colid)

    print_deleted(false_synonyms)
    to_delete_set = set(to_delete)
    return { colid: merge_taxon(taxon, false_synonyms) for colid, taxon in taxons.items() if taxon.colid not in to_delete_set}

def remove_dangling(taxons):
    accepted = set(taxon.accepted for colid, taxon in taxons.items() if taxon.accepted != None)
    parents = set(taxon.parent for colid, taxon in taxons.items() if taxon.parent != None)

    dangling_removed = { colid: taxon for colid, taxon in taxons.items() if colid in accepted or colid in parents or taxon.species_id != None }
    # If taxons were removed, then more taxons could be dangling
    if(len(dangling_removed) < len(taxons)):
        return remove_dangling(dangling_removed)
    else:
        return taxons

def remove_lonely_duplicates(taxons):
    accepted = set(taxon.accepted for colid, taxon in taxons.items() if taxon.accepted != None)
    parents = set(taxon.parent for colid, taxon in taxons.items() if taxon.parent != None)

    sorted_by_name = list(taxons.items())
    sorted_by_name.sort(key = lambda item: (item[1].name, item[1].rank, item[1].parent if item[1].parent != None else ""))
    updated = dict()
    for group in groupby(sorted_by_name, lambda item: (item[1].name, item[1].rank, item[1].parent if item[1].parent != None else "")):
        with_same_name = list(group[1])
        species_id = None
        keep = dict()
        if len(with_same_name) > 1:
            for colid, t in with_same_name:
                if colid in parents or colid in accepted:
                    keep[colid] = t
                # Loneley duplicate, can be dropped
                elif t.species_id != None:
                    species_id = t.species_id

            kept_but_no_species_id = next(((colid, k) for colid, k in keep.items() if k.species_id == None), None)
            if kept_but_no_species_id != None:
                keep[kept_but_no_species_id[0]] = dataclasses.replace(kept_but_no_species_id[1], species_id = species_id)
            updated.update(keep)
        else:
            updated.update(with_same_name)
    return updated

def export_taxons(filename, taxons):
    with open(filename, 'w+') as fd:
        wr = csv.writer(fd, delimiter='\t', quotechar='"')
        for colid, taxon in taxons.items():
            wr.writerow(taxon.as_row())

def main():
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    taxons = dict()

    for species_id, colid, sciname in read_taxon_tsv(in_file):
        get_taxon_hierarchy(colid, species_id, taxons)


    pruned_taxons = prune_taxons(taxons)
    accepted_taxons = delete_false_synonyms(pruned_taxons)

    no_loneley_taxons = remove_lonely_duplicates(accepted_taxons)
    for colid in set(accepted_taxons.keys()) - set(no_loneley_taxons.keys()):
        deleted = pruned_taxons[colid]
        print(f"{deleted.name} ({colid}, {deleted.species_id}) transfered to duplicate since it has no children")
    cleaned_taxons = remove_dangling(no_loneley_taxons)
    for colid, taxon in set(no_loneley_taxons.items()) - set(cleaned_taxons.items()):
        print(f"{taxon.name} ({colid}) deleted since it is no longer required")

    export_taxons(out_file, cleaned_taxons)

    return 0

if __name__ == '__main__':
    sys.exit(main())

