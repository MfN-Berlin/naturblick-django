from django.db import models

class Species(models.Model):
    sciname = models.CharField(max_length=255)

    def __str__(self):
        return self.sciname

