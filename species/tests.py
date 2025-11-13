from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Species, Group, SpeciesName, ImageFile, ImageCrop, DescMeta, PortraitImageFile, \
    Faunaportrait


class SpeciesTestCase(TestCase):
    def setUp(self):
        file_path = finders.find("test_amsel.jpg")

        with open(file_path, "rb") as f:
            test_amsel = SimpleUploadedFile(
                name="test_amsel.jpg",
                content=f.read(),
                content_type="image/jpeg"
            )

        Group.objects.create(name="bird")
        bird = Group.objects.get(name="bird")
        amsel = Species.objects.create(sciname="Turdus merula", group=bird, gername="Amsel", speciesid="bird_0")
        SpeciesName.objects.create(species=amsel, name="Schwarzdrossel", language="de")
        imagefile = ImageFile.objects.create(species=amsel, owner="Test", source="127.0.0.1", license="CC0",
                                             image=test_amsel)
        # remove in future
        pif = PortraitImageFile.objects.create(species=amsel, owner="Test", source="127.0.0.1", license="CC0",
                                               image=test_amsel)

        crop = ImageCrop.objects.create(imagefile=imagefile, cropping=None)
        amsel.avatar_new = crop
        amsel.save(update_fields=['avatar_new'])

        portrait = Faunaportrait.objects.create(species=amsel, language="de", short_description="Foobar",
                                                city_habitat="Foobar", published=True)
        DescMeta.objects.create(display_ratio="1:1", grid_ratio="1:1", text="Foobar", portrait=portrait,
                                portrait_image_file=pif, image_file=imagefile)

        for x in range(1, 11):
            Species.objects.create(sciname=f'foobar{x}', group=bird, speciesid=f'bird_{x}')

    def test_specieslist(self):
        url = reverse("species-filter")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
