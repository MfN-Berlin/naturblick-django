from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ForeignKey, URLField, OneToOneField, CharField, CASCADE
from django_currentuser.db.models import CurrentUserField
from image_cropping import ImageRatioField

from .choices import *
from .validators import min_max


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    nature = models.CharField(max_length=5, choices=NATURE_CHOICES)

    nature.short_description = "Nature"

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'group'


class Avatar(models.Model):
    image = models.ImageField(upload_to="avatars")
    image_owner = models.CharField(max_length=255)
    image_ownerLink = URLField(blank=True, null=True)
    image_source = URLField()
    image_license = models.CharField(max_length=64)
    cropping = ImageRatioField('image', '400x400', size_warning=True)

    def __str__(self):
        return self.image.name

    class Meta:
        db_table = 'avatar'


class Species(models.Model):
    speciesid = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='species')
    wikipedia = models.URLField(max_length=255, blank=True, null=True)
    nbclassid = models.CharField(max_length=255, blank=True, null=True)
    red_list_germany = models.CharField(max_length=255, blank=True, null=True, choices=REDLIST_CHOICES)
    iucncategory = models.CharField(max_length=2, blank=True, null=True, choices=IUCN_CHOICES)
    activity_start_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)
    activity_end_month = models.CharField(blank=True, null=True, max_length=9, choices=MONTH_CHOICES)
    activity_start_hour = models.IntegerField(blank=True, null=True,
                                              validators=[MinValueValidator(0), MaxValueValidator(23)])
    activity_end_hour = models.IntegerField(blank=True, null=True,
                                            validators=[MinValueValidator(0), MaxValueValidator(23)])
    avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, related_name='avatar', null="True", blank="True")
    female_avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, related_name='female_avatar', null="True",
                                      blank="True")
    gbifusagekey = models.IntegerField(blank=True, null=True)
    accepted = models.IntegerField(blank=True, null=True)
    created_by = CurrentUserField(related_name='species_created_by')
    updated_by = CurrentUserField(on_update=True, related_name='species_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return self.speciesid

    class Meta:
        db_table = 'species'
        verbose_name_plural = "species"


class SpeciesName(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='species_names')
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=2, choices=NAME_LANGUAGE_CHOICES)
    isPrimary = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'species_name'


class Portrait(models.Model):
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    species = models.OneToOneField(
        Species,
        on_delete=models.CASCADE,
        related_name="species"
    )
    short_description = models.TextField
    city_habitat = models.TextField
    human_interaction = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)

    short_description.help_text = "Kurze Beschreibung für den schnellen Überblick draußen."
    city_habitat.help_text = "Beschreibung Lebensraum in der Stadt, besondere Anpassungen an die Stadt."
    human_interaction.help_text = "Typische Interaktion mit dem Menschen, z.B. gestalterische Nutzung, Gefährdung durch menschliche Aktivität, Verbreitung."

    def __str__(self):
        return self.species.speciesid

    class Meta:
        db_table = 'portrait'


class Floraportrait(Portrait):
    leaf_description = models.TextField(default="")
    stem_axis_description = models.TextField(default="")
    flower_description = models.TextField(default="")
    fruit_description = models.TextField(default="")

    leaf_description.help_text = "Beschreibung Laubblatt: z.B. Form, Farbe, Blattstellung, besondere Merkmale."
    stem_axis_description.help_text = "Beschreibung Stängel/Stamm: z.B. Wuchsrichtung, Verzweigung, Farbe, besondere Merkmale."
    flower_description.help_text = "Beschreibung Blüte/Blütenstand: z.B. Farbe, Blütenstandsform, besondere Merkmale."
    fruit_description.help_text = "Bechreibung Frucht/Fruchstand: z.B. Form, Farbe, Oberfläche, besondere Merkmale."

    class Meta:
        db_table = 'flora_portrait'


class Faunaportrait(Portrait):
    male_description = models.TextField(blank=True, null=True)
    female_description = models.TextField(blank=True, null=True)
    juvenile_description = models.TextField(blank=True, null=True)
    tracks = models.TextField(blank=True, null=True)  # seems unused
    audioTitle = models.CharField(max_length=255, blank=True, null=True)
    audioLicense = models.CharField(max_length=255, blank=True, null=True)

    male_description.help_text = "Kurze Ergänzungen zu abweichenden Merkmalen der Männchen."
    female_description.help_text = "Kurze Ergänzungen zu abweichenden Merkmalen der Weibchen."
    juvenile_description.help_text = "Kurze Ergänzungen zu abweichenden Merkmalen der Jugendstadien."
    tracks.help_text = "Kurze Beschreibung zur Bestimmung anhand der Trittsiegel."

    class Meta:
        db_table = 'fauna_portrait'


class Source(models.Model):
    text = models.TextField(default="")
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)

    def __str__(self):
        return f"Source {self.text}"

    class Meta:
        db_table = 'source'


class GoodToKnow(models.Model):
    fact = models.TextField(default="")
    type = models.CharField(max_length=15, choices=GOOD_TO_KNOW_CHOICES)
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)

    def __str__(self):
        return f"GoodToKnow {self.fact}"

    class Meta:
        db_table = 'good_to_know'


class UnambigousFeature(models.Model):
    description = models.CharField(max_length=255)
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)


def __str__(self):
    return f"UnambigousFeature {self.description}"


class Meta:
    db_table = 'unambigous_feature'


class AdditionalLink(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(max_length=255)
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)

    def __str__(self):
        return f"AdditionalLink {self.title}"

    class Meta:
        db_table = 'additional_link'


class SimilarSpecies(models.Model):
    differences = models.TextField()
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)
    species = OneToOneField(Species,
                            on_delete=models.CASCADE,
                            parent_link=False)

    def __str__(self):
        return f"SimilarSpecies {self.species.speciesid}"

    class Meta:
        db_table = 'similar_species'


class Image(models.Model):
    image = models.ImageField(upload_to="portrait_images")
    image_owner = models.CharField(max_length=255)
    image_ownerLink = URLField(blank=True, null=True)
    image_source = URLField()
    image_license = models.CharField(max_length=64)

    def __str__(self):
        return f"Image {self.image_source}"

    class Meta:
        db_table = 'image'


class ImageText(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='image_texts')
    text = CharField(max_length=255)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)

    def __str__(self):
        return f"ImageText {self.text}"

    class Meta:
        db_table = 'image_text'


class PortraitImageInfo(models.Model):
    image_orientation = models.CharField(max_length=10, choices=IMAGE_ORIENTATION_CHOICES)
    display_ratio = models.CharField(max_length=3, choices=DISPLAY_RATIO_CHOICES)
    grid_ratio = models.CharField(max_length=3, choices=GRID_RATIO_CHOICES)
    focus_point_vertical = models.FloatField(validators=min_max(0.0, 100.0))
    focus_point_horizontal = models.FloatField(validators=min_max(0.0, 100.0))
    image = models.OneToOneField(Image, on_delete=CASCADE)

    def __str__(self):
        return f"PortraitImageInfo {self.image.image_source}"

    class Meta:
        db_table = 'portrait_image_info'


class PortraitImage(models.Model):
    species = models.OneToOneField(
        Species,
        on_delete=models.CASCADE,
        related_name="portrait_image"
    )
    description = models.OneToOneField(PortraitImageInfo, on_delete=models.SET_NULL, related_name="description",
                                       null=True)
    in_the_city = models.OneToOneField(PortraitImageInfo, on_delete=models.SET_NULL, related_name="in_the_city",
                                       null=True)
    fun_fact = models.OneToOneField(PortraitImageInfo, on_delete=models.SET_NULL, related_name="fun_fact", null=True)

    def __str__(self):
        return f"PortraitImage {self.species.speciesid}"

    class Meta:
        db_table = 'portrait_image'
