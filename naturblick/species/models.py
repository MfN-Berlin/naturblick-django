from django.db import models

# todos: Portrait, Flora/ Fauna -> multilingual, Names, Avatar, ..., speciesid autogenerate ffff
# check portraitfields


# blank     If True, the field is allowed to be blank.                          Default is False.
# null      If True, Django will store empty values as NULL in the database.    Default is False.

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Species(models.Model):
    speciesid = models.CharField(max_length=255, unique=True)
    sciname = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='speciess')
    gername = models.CharField(max_length=255, blank=True, null=True)
    engname = models.CharField(max_length=255, blank=True, null=True)
    easyname = models.CharField(max_length=255, blank=True, null=True)
    gbifusagekey = models.IntegerField(blank=True, null=True)
    accepted = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.sciname

class SpeciesName(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='species_names')
    name = models.CharField(max_length=255)

class Portrait(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='portraits')
    short_description = models.CharField(max_length=255)
    city_habitat = models.CharField(max_length=255)
    human_interaction = models.CharField(max_length=255, blank=True, null=True)
    link_to_wikipedia = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True

class Floraportrait(Portrait):
    leaf_description = models.CharField(max_length=255)
    stem_axis_description = models.CharField(max_length=255)
    flower_description = models.CharField(max_length=255)
    fruit_description = models.CharField(max_length=255)

class Faunaportrait(Portrait):
    male_description = models.CharField(max_length=255, blank=True, null=True)
    female_description = models.CharField(max_length=255, blank=True, null=True)
    juvenile_description = models.CharField(max_length=255, blank=True, null=True)




