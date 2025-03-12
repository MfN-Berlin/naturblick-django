from dataclasses import dataclass

mkeyGroups = ["amphibian",  # v0.0.1
              "bird",  # v0.0.1
              "butterfly",  # v0.0.1
              "gastropoda",  # v0.0.1
              "herb",  # v0.0.1
              "hymenoptera",  # v0.0.1
              "mammal",  # v0.0.1
              "reptile",  # v0.0.1
              "tree"]  # v0.0.1

char_names = [
    "gername",
    "engname",
    "gerdescription",
    "engdescription",
    "weight",
    "singleChoice",
    "value gername",
    "value engname",
    "value colors",
    "value dots",
    "value image"
]

# val id: Int,
# val gername: String,
# val engname: String,
# val group: String,
# val weight: Int,
# val singleChoice: Boolean?,
# val gerdescription: String? = null,
# val engdescription: String? = null
@dataclass
class Character:
    pass

# val id: Int,
# val character: Character,
# val gername: String,
# val engname: String,
# val colors: String?,
# val image: ImageFile?,
# val dots: String?
@dataclass
class CharacterValue:
    pass

# val characterValueId: Int, val speciesId: Int, val female: Boolean?, val weight: Int
@dataclass
class CharacterValueWeight:
    pass

@dataclass
class MatrixKeyTable:
    char_list: [Character]
    char_value_list: [CharacterValue]
    char_value_weights: [CharacterValueWeight]


# "CREATE TABLE `character` (`rowid` INTEGER NOT NULL, `gername` TEXT NOT NULL, `engname` TEXT NOT NULL, `group` TEXT NOT NULL, `weight` INTEGER NOT NULL, `single` INTEGER NOT NULL, `gerdescription` TEXT, `engdescription` TEXT, PRIMARY KEY(`rowid`));"
# "CREATE TABLE `character_value` (`rowid` INTEGER NOT NULL, `character_id` INTEGER NOT NULL, `gername` TEXT NOT NULL, `engname` TEXT NOT NULL, `has_image` INTEGER NOT NULL, PRIMARY KEY(`rowid`), FOREIGN KEY(`character_id`) REFERENCES `character`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
# "CREATE TABLE `character_value_species` (`rowid` INTEGER NOT NULL, `character_value_id` INTEGER NOT NULL, `species_id` INTEGER NOT NULL, `weight` INTEGER NOT NULL, `female` INTEGER, PRIMARY KEY(`rowid`), FOREIGN KEY(`character_value_id`) REFERENCES `character_value`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`species_id`) REFERENCES `species`(`rowid`) ON UPDATE NO ACTION ON DELETE CASCADE );"
def insert_characters(sqlite_cursor):
    pass

#       connection.prepareStatement("INSERT INTO character VALUES (?, ?, ?, ?, ?, ?, ? ,?);")
#                     .use { statement ->
#                         characters.forEach {
#                             it.prepare(statement)
#                         }
#                         statement.executeBatch()
#                     }
#                 connection.prepareStatement("INSERT INTO character_value VALUES (?, ?, ?, ?, ?);")
#                     .use { statement ->
#                         characterValues.forEach {
#                             it.prepare(statement)
#                         }
#                         statement.executeBatch()
#                     }
#                 connection.prepareStatement("""
#                     | INSERT INTO character_value_species (character_value_id, species_id, weight, female)
#                     | SELECT ?, COALESCE(s1.rowid, s.rowid), ?, ?
#                     | FROM species AS s
#                     | LEFT JOIN species AS s1 ON s1.rowid = s.accepted
#                     | WHERE s.rowid = ?;
#                 """.trimMargin())
#                     .use { statement ->
#                         characterValueWeights.forEach {
#                             it.prepare(statement)
#                         }
#                         statement.executeBatch()
#                     }
