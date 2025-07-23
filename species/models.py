import logging
import os

import requests
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ForeignKey, URLField, CASCADE
from django.db.models.constraints import UniqueConstraint
from django_currentuser.db.models import CurrentUserField
from image_cropping import ImageRatioField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from .choices import *
from .validators import min_max, validate_mp3

LARGE_WIDTH = 1200
MEDIUM_WIDTH = 800
SMALL_WIDTH = 400

logger = logging.getLogger("django")


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='German name')
    english_name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'tag'

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    nature = models.CharField(max_length=5, choices=NATURE_CHOICES, null=True)
    image = models.ImageField(upload_to="group_images", max_length=255, null=True, blank=True)
    svg = models.FileField(upload_to="group_svg", max_length=255, null=True, blank=True)

    nature.short_description = "Nature"

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'group'
        ordering = ['name']


class Avatar(models.Model):
    image = models.ImageField(upload_to="avatar_images", max_length=255)
    owner = models.CharField(max_length=255)
    owner_link = URLField(blank=True, null=True, max_length=255)
    source = URLField(max_length=1024)
    license = models.CharField(max_length=64)
    cropping = ImageRatioField('image', '400x400', size_warning=True)

    def __str__(self):
        return self.image.name

    class Meta:
        db_table = 'avatar'


class Species(models.Model):
    speciesid = models.CharField(max_length=255, unique=True)
    gername = models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name='German name')
    sciname = models.CharField(max_length=255, unique=True, db_index=True, verbose_name='Scientific name')
    engname = models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name='English name')
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    nbclassid = models.CharField(max_length=255, blank=True, null=True)
    wikipedia = models.URLField(max_length=255, blank=True, null=True, verbose_name='Wikipedia link')
    autoid = models.BooleanField(default=False)
    red_list_germany = models.CharField(max_length=255, blank=True, null=True, choices=REDLIST_CHOICES)
    iucncategory = models.CharField(max_length=2, blank=True, null=True, choices=IUCN_CHOICES)
    activity_start_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)
    activity_end_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)
    activity_start_hour = models.IntegerField(blank=True, null=True,
                                              validators=[MinValueValidator(0), MaxValueValidator(23)])
    activity_end_hour = models.IntegerField(blank=True, null=True,
                                            validators=[MinValueValidator(0), MaxValueValidator(23)])
    avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, related_name="avatar_species", null="True",
                               blank="True")
    female_avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, related_name="female_avatar_species",
                                      null="True", blank="True")
    gbifusagekey = models.IntegerField(blank=True, null=True, verbose_name='GBIF usagekey', unique=True)
    accepted_species = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)
    created_by = CurrentUserField(related_name='species_created_by_set', null=True)
    updated_by = CurrentUserField(on_update=True, related_name='species_updated_by_set', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tag = models.ManyToManyField(Tag, blank=True)

    plantnetpowoid = models.CharField(blank=True, null=True, max_length=255, unique=True)

    speciesid.short_description = "Species ID"

    def validate_gbif(self):
        if self.gbifusagekey:
            response = requests.get(f"https://api.gbif.org/v1/species/{self.gbifusagekey}")

            if response.status_code != 200:
                raise ValidationError({
                    "gbifusagekey": f"{self.gbifusagekey} could not be validated as a valid GBIF usage key (GBIF returned {response.status_code})"})

            json = response.json()

            is_species = json['rank'] == "SPECIES"
            is_accepted = not ('acceptedKey' in json)

            if not is_species:
                raise ValidationError({"gbifusagekey": "Only GBIF objects with rank SPECIES are valid"})
            if self.accepted_species:
                if is_accepted:
                    raise ValidationError(
                        {"gbifusagekey": "Accepted species must NOT be set for a GBIF species that is accepted"})
            else:
                if not is_accepted:
                    raise ValidationError(
                        {"gbifusagekey": "Accepted species must be set for a GBIF species that is NOT accepted"})
        else:

            if not self.id:
                raise ValidationError({"gbifusagekey": "All new species must have gbifusagekey set"})
            if self.accepted_species:
                raise ValidationError(
                    {"accepted_species": "Accepted species must NOT be set for a species without gbifusagekey"})

    def generate_id_for_new_species(self):
        if not self.speciesid:
            prefix = f'{self.group}_ffff'
            try:
                last_insert_id = Species.objects.filter(speciesid__startswith=prefix).order_by("-speciesid")[
                    0].speciesid
                next_insert_id = int(last_insert_id[len(last_insert_id) - 4: len(last_insert_id)], 16) + 1
                self.speciesid = f'{self.group}_ffff{next_insert_id:04x}'
            except:
                self.speciesid = f'{self.group}_ffff0000'

    def clean(self):
        super().clean()
        if self.accepted_species and self.accepted_species == self:
            raise ValidationError('Accepted species must not be self')
        if self.accepted_species and self.accepted_species.group != self.group:
            raise ValidationError('Accepted species must be in the same group')
        self.validate_gbif()
        self.generate_id_for_new_species()

    def __str__(self):
        name_list = [item for item in [self.gername, self.sciname, self.speciesid] if item is not None]
        return ' - '.join(name_list)

    class Meta:
        db_table = 'species'
        verbose_name_plural = "species"


class SpeciesName(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=4, choices=NAME_LANGUAGE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'species_name'
        constraints = [
            UniqueConstraint(
                fields=("species", "name", "language"), name="unique_species_name"
            ),
        ]


class PortraitImageFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    owner = models.CharField(max_length=255)
    owner_link = URLField(blank=True, null=True, max_length=255)
    source = URLField(max_length=1024)
    license = models.CharField(max_length=64)
    image = models.ImageField(upload_to="portrait_images", max_length=255, width_field='width', height_field='height')
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    @property
    def large(self):
        if self.width > LARGE_WIDTH:
            return self.image_large
        return None

    @property
    def medium(self):
        if self.width > MEDIUM_WIDTH:
            return self.image_medium
        return None

    @property
    def small(self):
        if self.width > SMALL_WIDTH:
            return self.image_small
        return None

    image_large = ImageSpecField(
        source='image',
        processors=[ResizeToFit(LARGE_WIDTH, None)],
        options={'quality': 90}
    )
    image_medium = ImageSpecField(
        source='image',
        processors=[ResizeToFit(MEDIUM_WIDTH, None)],
        options={'quality': 90}
    )
    image_small = ImageSpecField(
        source='image',
        processors=[ResizeToFit(SMALL_WIDTH, None)],
        options={'quality': 90}
    )

    def __str__(self):
        return f"{self.owner} {self.image.name[self.image.name.index('/') + 1:]}"

    def clean(self):
        super().clean()
        desc = DescMeta.objects.filter(portrait_image_file=self.id).first()
        if desc and desc.portrait.species != self.species:
            raise ValidationError(
                f"This Image is already set as a 'description' in the portrait of {desc.portrait.species}. The species can not be changed until it's unset")

        funfact = FunFactMeta.objects.filter(portrait_image_file=self.id).first()
        if funfact and funfact.portrait.species != self.species:
            raise ValidationError(
                f"This Image is already set as a 'fun fact' in the portrait of {funfact.portrait.species}. The species can not be changed until it's unset")

        inthecity = InTheCityMeta.objects.filter(portrait_image_file=self.id).first()
        if inthecity and inthecity.portrait.species != self.species:
            raise ValidationError(
                f"This Image is already set as an 'in the city' in the portrait of {funfact.portrait.species}. The species can not be changed until it's unset")

    class Meta:
        db_table = 'portrait_image_file'


class PortraitImageMeta(models.Model):
    image_orientation = models.CharField(max_length=10, choices=IMAGE_ORIENTATION_CHOICES,
                                         null=True)  # this should be not null
    display_ratio = models.CharField(max_length=3, choices=DISPLAY_RATIO_CHOICES)
    grid_ratio = models.CharField(max_length=3, choices=GRID_RATIO_CHOICES)
    focus_point_vertical = models.FloatField(validators=min_max(0.0, 100.0),
                                             null=True)  # one of the focus_point shouldn't be null -> better only one field non nullable
    focus_point_horizontal = models.FloatField(validators=min_max(0.0, 100.0), null=True)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.text}"

    class Meta:
        abstract = True


class Portrait(models.Model):
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT
    )
    language = models.CharField(max_length=4, choices=LANGUAGE_CHOICES)
    short_description = models.TextField()
    city_habitat = models.TextField()
    human_interaction = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)
    ecosystem_role = models.TextField(blank=True, null=True)

    short_description.help_text = "Kurze Beschreibung für den schnellen Überblick draußen."
    city_habitat.help_text = "Beschreibung Lebensraum in der Stadt, besondere Anpassungen an die Stadt."
    human_interaction.help_text = "Typische Interaktion mit dem Menschen, z.B. gestalterische Nutzung, Gefährdung durch menschliche Aktivität, Verbreitung."

    @property
    def db_in_the_city(self):
        in_the_city = self.city_habitat
        if self.human_interaction:
            in_the_city += f"\n\n{self.human_interaction}"
        return in_the_city

    @property
    def db_sources(self):
        source_texts = [s.strip() for s in self.source_set.all().values_list('text', flat=True)]
        return '\n\n'.join(source_texts) if source_texts else None

    def __str__(self):
        return self.species.speciesid

    class Meta:
        db_table = 'portrait'
        constraints = [
            UniqueConstraint(fields=['species', 'language'], name='unique_species_language')
        ]


class DescMeta(PortraitImageMeta):
    portrait = models.OneToOneField(Portrait, on_delete=CASCADE)
    portrait_image_file = models.ForeignKey(PortraitImageFile, on_delete=CASCADE)

    def clean(self):
        super().clean()
        if self.portrait and self.portrait_image_file and self.portrait.species.speciesid != self.portrait_image_file.species.speciesid:
            raise ValidationError("DescriptionImage species must be same as portrait species")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = 'desc_meta'


class FunFactMeta(PortraitImageMeta):
    portrait = models.OneToOneField(Portrait, on_delete=CASCADE)
    portrait_image_file = models.ForeignKey(PortraitImageFile, on_delete=CASCADE)

    def clean(self):
        super().clean()
        if self.portrait and self.portrait_image_file and self.portrait.species.speciesid != self.portrait_image_file.species.speciesid:
            raise ValidationError("FunFactImage species must be same as portrait species")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = 'funfact_meta'


class InTheCityMeta(PortraitImageMeta):
    portrait = models.OneToOneField(Portrait, on_delete=CASCADE)
    portrait_image_file = models.ForeignKey(PortraitImageFile, on_delete=CASCADE)

    def clean(self):
        super().clean()
        if self.portrait and self.portrait_image_file and self.portrait.species.speciesid != self.portrait_image_file.species.speciesid:
            raise ValidationError("InTheCityImage species must be same as portrait species")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = 'inthecity_meta'


class Floraportrait(Portrait):
    leaf_description = models.TextField()
    stem_axis_description = models.TextField()
    flower_description = models.TextField()
    fruit_description = models.TextField()

    leaf_description.help_text = "Beschreibung Laubblatt: z.B. Form, Farbe, Blattstellung, besondere Merkmale."
    stem_axis_description.help_text = "Beschreibung Stängel/Stamm: z.B. Wuchsrichtung, Verzweigung, Farbe, besondere Merkmale."
    flower_description.help_text = "Beschreibung Blüte/Blütenstand: z.B. Farbe, Blütenstandsform, besondere Merkmale."
    fruit_description.help_text = "Bechreibung Frucht/Fruchstand: z.B. Form, Farbe, Oberfläche, besondere Merkmale."

    @property
    def db_description(self):
        return f"{self.short_description}\n\n{self.leaf_description}\n\n{self.stem_axis_description}\n\n{self.flower_description}\n\n{self.fruit_description}"

    class Meta:
        db_table = 'floraportrait'


class FaunaportraitAudioFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    owner = models.CharField(max_length=255)
    owner_link = URLField(blank=True, null=True, max_length=255)
    source = URLField(max_length=1024)
    license = models.CharField(max_length=64)
    audio_file = models.FileField(upload_to="audio_files", validators=[validate_mp3])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.species.group.nature != 'fauna':
            raise ValidationError('FaunaPortraitAudioFiles only for fauna')
        if self.id is not None:
            faunaportrait = Faunaportrait.objects.filter(faunaportrait_audio_file=self.id).first()
            if faunaportrait and faunaportrait.species != self.species:
                raise ValidationError(
                    f"This Audiofile is already set as an 'audiofile' in the portrait of {faunaportrait}. The species can not be changed until it's unset")

    def __str__(self):
        return f"{self.owner} {os.path.basename(self.audio_file.path)}"

    class Meta:
        db_table = 'faunaportrait_audio_file'


class Faunaportrait(Portrait):
    male_description = models.TextField(blank=True, null=True)
    female_description = models.TextField(blank=True, null=True)
    juvenile_description = models.TextField(blank=True, null=True)
    tracks = models.TextField(blank=True, null=True)  # seems unused
    audio_title = models.CharField(max_length=255, blank=True, null=True)
    faunaportrait_audio_file = models.ForeignKey(FaunaportraitAudioFile, on_delete=models.SET_NULL, null=True,
                                                 blank=True)

    male_description.help_text = "Kurze Ergänzungen zu abweichenden Merkmalen der Männchen."
    female_description.help_text = "Kurze Ergänzungen zu abweichenden Merkmalen der Weibchen."
    juvenile_description.help_text = "Kurze Ergänzungen zu abweichenden Merkmalen der Jugendstadien."
    tracks.help_text = "Kurze Beschreibung zur Bestimmung anhand der Trittsiegel."

    def clean(self):
        super().clean()
        if self.faunaportrait_audio_file and self.species.speciesid != self.faunaportrait_audio_file.species.speciesid:
            raise ValidationError("Audiofile species must be same as faunaportrait species")

        if (self.faunaportrait_audio_file and not self.audio_title) or (
                not self.faunaportrait_audio_file and self.audio_title):
            raise ValidationError("Audiofile and audiotitle must be both set or not")

    @property
    def db_description(self):
        description = self.short_description
        if self.male_description:
            description += f"\n\n{self.male_description}"
        if self.female_description:
            description += f"\n\n{self.female_description}"
        if self.juvenile_description:
            description += f"\n\n{self.juvenile_description}"
        return description

    class Meta:
        db_table = 'faunaportrait'


class Source(models.Model):
    text = models.TextField()
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return f"Source {self.text}"

    class Meta:
        db_table = 'source'


class GoodToKnow(models.Model):
    fact = models.TextField()
    type = models.CharField(max_length=15, choices=GOOD_TO_KNOW_CHOICES)
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return f"GoodToKnow {self.fact}"

    class Meta:
        db_table = 'good_to_know'


class UnambigousFeature(models.Model):
    description = models.TextField()
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return f"UnambigousFeature {self.description}"

    class Meta:
        db_table = 'unambigous_feature'


class AdditionalLink(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(max_length=255)
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return f"AdditionalLink {self.title}"

    class Meta:
        db_table = 'additional_link'


class SimilarSpecies(models.Model):
    differences = models.TextField()
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)
    species = ForeignKey(Species,
                         on_delete=models.CASCADE,
                         parent_link=False)
    order = models.IntegerField()

    @property
    def has_portrait(self):
        return self.species.portrait_set.exists()

    def clean(self):
        super().clean()
        if self.species == self.portrait.species:
            raise ValidationError('Yes, this species will probably be similar to itself')

        if self.species.group != self.portrait.species.group:
            raise ValidationError('A similar species should be part of the same group')

    def __str__(self):
        return f"SimilarSpecies {self.species.speciesid}"

    class Meta:
        db_table = 'similar_species'


class SourcesImprint(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32, choices=SOURCES_IMPRINT_CHOICES, verbose_name='Group')
    scie_name = models.CharField(max_length=255, verbose_name='German description')
    scie_name_eng = models.CharField(max_length=255, null=True, blank=True, verbose_name='English description')
    image_source = models.CharField(max_length=255, null=True, blank=True)
    image_link = models.CharField(max_length=255, null=True, blank=True)
    licence = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'sources_imprint'

    def __str__(self):
        return self.scie_name


class SourcesTranslation(models.Model):
    language = models.CharField(max_length=4, choices=NAME_LANGUAGE_CHOICES)
    key = models.CharField(max_length=255, choices=SOURCES_TRANSLATION_CHOICES)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'sources_translation'

    def __str__(self):
        return f"{self.key} - {self.value}"


class PlantnetPowoidMapping(models.Model):
    plantnetpowoid = models.CharField(blank=True, null=True, max_length=255, unique=True)
    species_plantnetpowoid = models.ForeignKey(Species, to_field="plantnetpowoid",
                                               limit_choices_to={"plantnetpowoid__isnull": False}, on_delete=CASCADE)

    class Meta:
        db_table = "plantnet_powoid_mapping"

    def __str__(self):
        return f"{self.plantnetpowoid} => {self.species_plantnetpowoid.plantnetpowoid} [{self.species_plantnetpowoid}]"
