from django.db import models

class Species(models.Model):
    speciesid = models.CharField(max_length=255, unique=True)
    sciname = models.CharField(max_length=255)
    group = models.CharField(max_length=255, null=False, default="none")
    gername = models.CharField(max_length=255, blank=True, null=True)
    engname = models.CharField(max_length=255, blank=True, null=True)
    easyname = models.CharField(max_length=255, blank=True, null=True)
    gbifusagekey = models.IntegerField(blank=True, null=True)
    accepted = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.sciname

