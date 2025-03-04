from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ForeignKey, URLField, CASCADE
from django.utils.safestring import mark_safe
from django_currentuser.db.models import CurrentUserField
from image_cropping import ImageRatioField

from .choices import *
from .validators import min_max, validate_png, validate_mp3


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    english_name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'tag'

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    nature = models.CharField(max_length=5, choices=NATURE_CHOICES, null=True)

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

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.image))

    thumbnail.short_description = 'Thumbnail'
    thumbnail.allow_tags = True

    def __str__(self):
        return self.image.name

    class Meta:
        db_table = 'avatar'


class Species(models.Model):
    speciesid = models.CharField(max_length=255, unique=True)
    gername = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    sciname = models.CharField(max_length=255, unique=True, db_index=True)
    engname = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    nbclassid = models.CharField(max_length=255, blank=True, null=True)
    autoid = models.BooleanField(default=False)
    red_list_germany = models.CharField(max_length=255, blank=True, null=True, choices=REDLIST_CHOICES)
    iucncategory = models.CharField(max_length=2, blank=True, null=True, choices=IUCN_CHOICES)
    activity_start_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)
    activity_end_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)
    activity_start_hour = models.IntegerField(blank=True, null=True,
                                              validators=[MinValueValidator(0), MaxValueValidator(23)])
    activity_end_hour = models.IntegerField(blank=True, null=True,
                                            validators=[MinValueValidator(0), MaxValueValidator(23)])
    avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, related_name='+', null="True", blank="True")
    female_avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, related_name='+', null="True",
                                      blank="True")
    gbifusagekey = models.IntegerField(blank=True, null=True)
    accepted_species = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)
    created_by = CurrentUserField(related_name='species_created_by_set', null=True)
    updated_by = CurrentUserField(on_update=True, related_name='species_updated_by_set', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tag = models.ManyToManyField(Tag, blank=True)

    speciesid.short_description = "Species ID"

    def save(self, *args, **kwargs):
        if not self.speciesid:
            prefix = f'{self.group}_ffff'
            try:
                last_insert_id = Species.objects.filter(speciesid__startswith=prefix).order_by("-speciesid")[
                    0].speciesid
                next_insert_id = int(last_insert_id[len(last_insert_id) - 4: len(last_insert_id)], 16) + 1
                self.speciesid = f'{self.group}_ffff{next_insert_id:04x}'
            except:
                self.speciesid = f'{self.group}_ffff0000'
        super().save(*args, **kwargs)

    def __str__(self):
        name_list = [item for item in [self.gername, self.sciname, self.speciesid] if item is not None]
        return ' - '.join(name_list)

    class Meta:
        db_table = 'species'
        verbose_name_plural = "species"


class SpeciesName(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=2, choices=NAME_LANGUAGE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'species_name'


class PortraitImageFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    owner = models.CharField(max_length=255)
    owner_link = URLField(blank=True, null=True, max_length=255)
    source = URLField(max_length=1024)
    license = models.CharField(max_length=64)
    image = models.ImageField(upload_to="portrait_images", max_length=255)

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
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    short_description = models.TextField()
    city_habitat = models.TextField()
    human_interaction = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)

    short_description.help_text = "Kurze Beschreibung für den schnellen Überblick draußen."
    city_habitat.help_text = "Beschreibung Lebensraum in der Stadt, besondere Anpassungen an die Stadt."
    human_interaction.help_text = "Typische Interaktion mit dem Menschen, z.B. gestalterische Nutzung, Gefährdung durch menschliche Aktivität, Verbreitung."

    def __str__(self):
        return self.species.speciesid

    class Meta:
        db_table = 'portrait'
        constraints = [
            models.UniqueConstraint(fields=['species', 'language'], name='unique_species_language')
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

    class Meta:
        db_table = 'floraportrait'


class FaunaportraitAudioFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    owner = models.CharField(max_length=255)
    owner_link = URLField(blank=True, null=True, max_length=255)
    source = URLField(max_length=1024)
    license = models.CharField(max_length=64)
    audio_file = models.FileField(upload_to="audio_files", null=True, blank=True, validators=[validate_mp3])
    audio_spectrogram = models.ImageField(upload_to="spectrogram_images", null=True, blank=True,
                                          validators=[validate_png])

    def clean(self):
        super().clean()
        if self.id is not None:
            faunaportrait = Faunaportrait.objects.filter(faunaportrait_audio_file=self.id).first()
            if faunaportrait and faunaportrait.species != self.species:
                raise ValidationError(
                    f"This Audiofile is already set as an 'audiofile' in the portrait of {faunaportrait}. The species can not be changed until it's unset")

    def __str__(self):
        return f"{self.owner} {self.audio_file.name[self.audio_file.name.index('/') + 1:]}"

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

        if (self.faunaportrait_audio_file and not self.audio_title) or (not self.faunaportrait_audio_file and self.audio_title):
            raise ValidationError("Audiofile and audiotitle must be both set or not")

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

    def __str__(self):
        return f"SimilarSpecies {self.species.speciesid}"

    class Meta:
        db_table = 'similar_species'


class Character(models.Model):
    id = models.BigAutoField(primary_key=True)
    gername = models.CharField(max_length=255)
    engname = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    weight = models.IntegerField()
    single_choice = models.BooleanField(null=True, blank=True)
    gerdescription = models.TextField(null=True, blank=True)
    engdescription = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'character'

    def __str__(self):
        return self.gername


class CharacterValue(models.Model):
    id = models.BigAutoField(primary_key=True)
    character = models.ForeignKey(Character, on_delete=CASCADE)
    gername = models.CharField(max_length=255)
    engname = models.CharField(max_length=255)
    colors = models.CharField(max_length=255, null=True, blank=True)
    dots = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="character_images", max_length=255, null=True)

    class Meta:
        db_table = 'character_value'

    def __str__(self):
        return self.gername


class SourcesImprint(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32, choices=SOURCES_IMPRINT_CHOICES)
    scie_name = models.CharField(max_length=255)
    scie_name_eng = models.CharField(max_length=255, null=True, blank=True)
    image_source = models.CharField(max_length=255, null=True, blank=True)
    image_link = models.CharField(max_length=255, null=True, blank=True)
    licence = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'sources_imprint'

    def __str__(self):
        return self.scie_name


class SourcesTranslation(models.Model):
    language = models.CharField(max_length=2, choices=NAME_LANGUAGE_CHOICES)
    key = models.CharField(max_length=255, choices=SOURCES_TRANSLATION_CHOICES)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'sources_translation'

    def __str__(self):
        return f"{self.key} - {self.value}"
