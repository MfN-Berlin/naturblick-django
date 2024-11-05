from django.db.models.lookups import Range
from django.test import TestCase

from .models import Species, Group


class SpeciesTestCase(TestCase):
    def test_speciesid_algorithm(self):
        """Species with automatically created speciesids"""
        Group.objects.create(name="bird")
        bird = Group.objects.get(name="bird")
        Species.objects.create(sciname="Turdus merula", group=bird)
        for x in range(1,11):
            Species.objects.create(sciname=f'foobar{x}', group=bird)
        amsel = Species.objects.get(sciname="Turdus merula")
        foobar1 = Species.objects.get(sciname="foobar1")
        foobarA = Species.objects.get(sciname="foobar10")
        self.assertEqual(amsel.speciesid, 'bird_ffff0000')
        self.assertEqual(foobar1.speciesid, 'bird_ffff0001')
        self.assertEqual(foobarA.speciesid, 'bird_ffff000a')