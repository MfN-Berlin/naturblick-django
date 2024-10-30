from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_currentuser.db.models import CurrentUserField

# todos: Portrait, Flora/ Fauna -> multilingual, Names, Avatar, ..., speciesid autogenerate ffff
# check portraitfields

class Group(models.Model):
    NATURE_CHOICES = [
        ('Fauna', 'Fauna'),
        ('Flora', 'Flora'),
    ]

    name = models.CharField(max_length=255, unique=True)
    nature = models.CharField(max_length=5, choices=NATURE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'group'

 # id                 | integer                  |           | not null | nextval('species_id_seq'::regclass)
 # speciesid          | character varying(255)   |           | not null |
 # sciname            | character varying(255)   |           | not null |
 # gername            | character varying(255)   |           |          |
 # ? pageName           | character varying(255)   |           | not null |
 # ! scinamesynonym     | character varying(255)   |           |          |
 # -> names gernamesynonym     | character varying(255)   |           |          |
 # ! group              | character varying(255)   |           | not null |
 # ! phenotypefemaleid  | character varying(255)   |           |          |
 # naturblickidkey    | boolean                  |           | not null |
 # portrait           | boolean                  |           | not null |
 # imageexists        | boolean                  |           | not null |
 # wikipedia          | character varying(255)   |           |          |
 # autoid             | boolean                  |           | not null |
 # ! nbclassid          | character varying(255)   |           |          |
 # innaturblick       | boolean                  |           | not null |
 # -> namesengname            | character varying(255)   |           |          |
 # -> names easyname           | character varying(255)   |           |          |
 # ! scientificAuthors  | character varying(255)   |           |          |
 # ! order              | character varying(255)   |           |          |
 # ! family             | character varying(255)   |           |          |
 # ! genus              | character varying(255)   |           |          |
 # ! redListGermany     | character varying(255)   |           |          |
 # ! iucncategory       | character varying(255)   |           |          |
 # ! activityStartMonth | character varying(255)   |           |          |
 # ! activityEndMonth   | character varying(255)   |           |          |
 # ! activityStartHour  | integer                  |           |          |
 # ! activityEndHour    | integer                  |           |          |
 # ! gbifusagekey       | integer                  |           |          |
 # ! accepted           | integer                  |           |          |

class Species(models.Model):
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]

    IUCN_CHOICES = [
        ('NE', 'NE'),
        ('DD', 'DD'),
        ('LC', 'LC'),
        ('NT', 'NT'),
        ('VU', 'VU'),
        ('EN', 'EN'),
        ('CR', 'CR'),
        ('EW', 'EW'),
        ('EX', 'EX'),
    ]

    REDLIST_CHOICES = [
        ('gefahrdet', 'gefährdet'),
        ('Vorwarnliste', 'Vorwarnliste'),
        ('ausgestorben oder verschollen', 'ausgestorben oder verschollen'),
        ('vomAussterbenBedroht', 'vom Aussterben bedroht'),
        ('starkGefahrdet', 'stark gefährdet'),
        ('GefahrdungUnbekanntenAusmasses', 'Gefährdung unbekannten Ausmasses'),
        ('extremSelten', 'extrem selten'),
        ('DatenUnzureichend', 'Daten unzureichend'),
        ('ungefahrdet', 'ungefährdet'),
        ('nichtBewertet', 'nicht bewertet'),
        ('keinNachweis', 'kein Nachweis'),
    ]

    speciesid = models.CharField(max_length=255, unique=True)   # in ktor
    sciname = models.CharField(max_length=255)                  # in ktor
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='species') # in ktor
    wikipedia = models.URLField(max_length=255, blank=True, null=True) # in ktor
    name = models.CharField(max_length=255, blank=True, null=True) # in ktor
    nbclassid = models.CharField(max_length=255, blank=True, null=True) # playback
    red_list_germany = models.CharField(max_length=255, blank=True, null=True, choices=REDLIST_CHOICES)     # in ktor
    iucncategory = models.CharField(max_length=2, blank=True, null=True, choices=IUCN_CHOICES)              # in ktor
    activity_start_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)     # playback
    activity_end_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)       # playback
    activity_start_hour = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(23)])  # playback
    activity_end_hour = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(23)])    # playback
    gbifusagekey = models.IntegerField(blank=True, null=True)  # orga
    accepted = models.IntegerField(blank=True, null=True)  # in ktor
    created_by = CurrentUserField(related_name='species_created_by')  # orga
    updated_by = CurrentUserField(on_update=True, related_name='species_updated_by')  # orga
    created_at = models.DateTimeField(auto_now_add=True)  # orga
    updated_at = models.DateTimeField(auto_now=True)  # orga

    def __str__(self):
        return self.sciname

    def save(self, *args, **kwargs):
        if not self.speciesid:
            prefix = f'{self.group}_ffff'
            try:
                last_insert_id = Species.objects.filter(speciesid__startswith=prefix).order_by("-speciesid")[0].speciesid
                next_insert_id = int(last_insert_id[len(last_insert_id) - 4: len(last_insert_id)], 16) + 1
                self.speciesid = f'{self.group}_ffff{next_insert_id:04x}'
            except:
                self.speciesid = f'{self.group}_ffff0000'
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'species'

class SpeciesName(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='species_names')
    name = models.CharField(max_length=255)
    # LANGUAGE ?!

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'species_name'

class Portrait(models.Model):
    short_description = models.TextField
    city_habitat = models.TextField
    human_interaction = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)

    class Meta:
        abstract = True

# ! shortDescription    | text                     |           | not null |
# ! leafDescription     | text                     |           | not null |
# ! stemAxisDescription | text                     |           | not null |
# ! flowerDescription   | text                     |           | not null |
# ! fruitDescription    | text                     |           | not null |
# ! cityHabitat         | text                     |           | not null |
# ! humanInteraction    | text                     |           |          |
# ! linkToWikipedia     | character varying(255)   |           |          |
# ? language            | integer                  |           |          |
# ! created_by          | integer                  |           |          |
# ! updated_by          | integer                  |           |          |
# ! created_at          | timestamp with time zone |           |          | CURRENT_TIMESTAMP
# ! updated_at          | timestamp with time zone |           |          | CURRENT_TIMESTAMP
#  preview             | boolean                  |           | not null |
#  ! name                | character varying(255)   |           |          |
#  images              | integer                  |           |          |
#  published_at        | timestamp with time zone |           |          |

class Floraportrait(Portrait):
    species = models.OneToOneField(
        Species,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    leaf_description = models.TextField
    stem_axis_description = models.TextField
    flower_description = models.TextField
    fruit_description = models.TextField

    def __str__(self):
        return self.species.name

    class Meta:
        db_table = 'flora_portrait'

 # ! shortDescription    | text                     |           | not null |
 # ! maleDescription     | text                     |           |          |
 # ! femaleDescription   | text                     |           |          |
 # ! juvenileDescription | text                     |           |          |
 # ! cityHabitat         | text                     |           | not null |
 # ! humanInteraction    | text                     |           |          |
 # ! linkToWikipedia     | character varying(255)   |           |          |
 # ! preview             | boolean                  |           | not null |
 # ! tracks              | text                     |           |          |
 # ! name                | character varying(255)   |           |          |
 # images              | integer                  |           |          |
 # published_at        | timestamp with time zone |           |          |
 # ! audioTitle          | character varying(255)   |           |          |
 # ! audioLicense        | character varying(255)   |           |          |

class Faunaportrait(Portrait):
    species = models.OneToOneField(
        Species,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    male_description = models.TextField(blank=True, null=True)
    female_description = models.TextField(blank=True, null=True)
    juvenile_description = models.TextField(blank=True, null=True)
    tracks = models.TextField(blank=True, null=True)
    audioTitle = models.CharField(max_length=255, blank=True, null=True)
    audioLicense = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.species.name

    class Meta:
        db_table = 'fauna_portrait'

