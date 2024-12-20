from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ForeignKey, URLField
from django_currentuser.db.models import CurrentUserField
from image_cropping import ImageRatioField
from .choices import *


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
    image_owner = models.CharField(max_length=256)
    image_ownerLink = URLField(blank=True, null=True)
    image_source = URLField()
    image_license = models.CharField(max_length=64)
    cropping = ImageRatioField('image', '400x400', size_warning=True)

    def __str__(self):
        return self.image.name


class Species(models.Model):
    speciesid = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='species')
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
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='avatar', null="True", blank="True")
    female_avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='female_avatar', null="True",
                                      blank="True")
    gbifusagekey = models.IntegerField(blank=True, null=True)
    accepted = models.IntegerField(blank=True, null=True)
    created_by = CurrentUserField(related_name='species_created_by')
    updated_by = CurrentUserField(on_update=True, related_name='species_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.speciesid

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

    class Meta:
        db_table = 'species'
        verbose_name_plural = "species"


class SpeciesName(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='species_names')
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    isPrimary = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'species_name'


class Portrait(models.Model):
    species = models.OneToOneField(
        Species,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="species"
    )
    short_description = models.TextField
    city_habitat = models.TextField
    human_interaction = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.species.speciesid


class Floraportrait(Portrait):
    leaf_description = models.TextField(default="")
    stem_axis_description = models.TextField(default="")
    flower_description = models.TextField(default="")
    fruit_description = models.TextField(default="")

    class Meta:
        db_table = 'flora_portrait'


class Faunaportrait(Portrait):
    male_description = models.TextField(blank=True, null=True)
    female_description = models.TextField(blank=True, null=True)
    juvenile_description = models.TextField(blank=True, null=True)
    tracks = models.TextField(blank=True, null=True)  # seems unused
    audioTitle = models.CharField(max_length=255, blank=True, null=True)
    audioLicense = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'fauna_portrait'


class Source(models.Model):
    text = models.TextField(default="")
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class GoodToKnow(models.Model):
    fact = models.TextField(default="")
    type = models.CharField(max_length=3, choices=GOOD_TO_KNOW_CHOICES)
    portrait = ForeignKey(Portrait, on_delete=models.CASCADE)

    def __str__(self):
        return self.fact
