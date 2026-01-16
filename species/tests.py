import json

from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import (
    Species,
    Group,
    SpeciesName,
    ImageFile,
    ImageCrop,
    DescMeta,
    PortraitImageFile,
    Faunaportrait,
    Tag,
    PlantnetPowoidMapping,
    LeichtPortrait,
    LeichtRecognize,
    LeichtGoodToKnow,
)


def load_static_image(content_type="image/jpeg", file_name="test_amsel.jpg"):
    file_path = finders.find(file_name)

    with open(file_path, "rb") as f:
        return SimpleUploadedFile(
            name=file_name, content=f.read(), content_type=content_type
        )


class SpeciesTestCase(TestCase):
    def setUp(self):
        test_amsel = load_static_image("test_amsel")

        Group.objects.create(name="bird", nature="fauna")
        bird = Group.objects.get(name="bird")
        amsel = Species.objects.create(
            sciname="Turdus merula",
            group=bird,
            gername="Amsel",
            speciesid="bird_0",
            plantnetpowoid="4321-5",
        )
        SpeciesName.objects.create(species=amsel, name="Schwarzdrossel", language="de")
        imagefile = ImageFile.objects.create(
            species=amsel,
            owner="Test",
            source="127.0.0.1",
            license="CC0",
            image=test_amsel,
        )
        # remove in future
        pif = PortraitImageFile.objects.create(
            species=amsel,
            owner="Test",
            source="127.0.0.1",
            license="CC0",
            image=test_amsel,
        )

        crop = ImageCrop.objects.create(imagefile=imagefile, cropping=None)
        amsel.avatar_new = crop
        amsel.save(update_fields=["avatar_new"])

        portrait = Faunaportrait.objects.create(
            species=amsel,
            language="de",
            short_description="Foobar",
            city_habitat="Foobar",
            published=True,
        )
        DescMeta.objects.create(
            display_ratio="1:1",
            grid_ratio="1:1",
            text="Foobar",
            portrait=portrait,
            portrait_image_file=pif,
            image_file=imagefile,
        )

        amsel_tag = Tag.objects.create(name="Vogel", english_name="Bird")
        Tag.objects.create(name="nachtaktiv", english_name="nocturnal")
        amsel.tag.add(amsel_tag)

        PlantnetPowoidMapping.objects.create(
            plantnetpowoid="1234-1", species_plantnetpowoid=amsel
        )

        # Leicht
        leicht_portrait = LeichtPortrait.objects.create(
            name="Vogel", avatar=crop, goodtoknow_image=imagefile
        )
        LeichtRecognize(text="foo", portrait=leicht_portrait, ordering=1)
        LeichtGoodToKnow(text="foo", portrait=leicht_portrait, ordering=1)

    def test_speciesfilter_ok(self):
        url = reverse("species-filter")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].get("localname"), "Amsel")

    def test_specieslist_ok(self):
        url = reverse("species-list")
        response = self.client.get(url, query_params={"speciesid_in": "bird_0"})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].get("localname"), "Amsel")

    def test_specieslist_not_found(self):
        url = reverse("species-list")
        response = self.client.get(url, query_params={"speciesid_in": "bird_foo"})
        self.assertEqual(response.status_code, 404)

    def test_species_ok(self):
        url = reverse("species", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content.get("localname"), "Amsel")

    def test_portrait_detail_ok(self):
        url = reverse("portrait-detail")
        response = self.client.get(url, query_params={"id": "1"})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content.get("localname"), "Amsel")

    def test_tags_filter(self):
        url = reverse("tags-filter")
        response = self.client.get(url)
        content = json.loads(response.content)
        self.assertEqual(len(content), 2)

        response = self.client.get(url, query_params={"tagsearch": "Vogel"})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].get("localname"), "Vogel")

    def test_app_content_db(self):
        url = reverse("app-content-db")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_app_content_leicht_db(self):
        url = reverse("app-content-leicht-db")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tags(self):
        url = reverse("tags")
        response = self.client.get(url, query_params={"tag": ["1", "2"]})
        content = json.loads(response.content)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0].get("localname"), "Vogel")

    def test_groups(self):
        url = reverse("groups")
        response = self.client.get(url)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].get("name"), "bird")
