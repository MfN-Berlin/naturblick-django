from admin_ordering.admin import OrderableAdmin
from django import forms
from django.contrib import admin, messages
from django.db import models, transaction
from django.db.models import Q
from django.forms import Textarea
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.html import mark_safe
from django.utils.translation import ngettext
from image_cropping import ImageCroppingMixin
from image_cropping.utils import get_backend
from imagekit import ImageSpec
from imagekit.admin import AdminThumbnail
from imagekit.cachefiles import ImageCacheFile
from imagekit.processors import ResizeToFit
from django.core.exceptions import ValidationError


from species import utils
from .models import Species, SpeciesName, Source, GoodToKnow, SimilarSpecies, AdditionalLink, UnambigousFeature, \
    PortraitImageFile, DescMeta, FunFactMeta, InTheCityMeta, Faunaportrait, Avatar, Group, Floraportrait, \
    Tag, SourcesImprint, SourcesTranslation, FaunaportraitAudioFile, PlantnetPowoidMapping, Portrait, LeichtPortrait, \
    LeichtRecognize, LeichtGoodToKnow


class AdminThumbnailSpec(ImageSpec):
    processors = [ResizeToFit(150, None)]
    format = 'JPEG'
    options = {'quality': 60}


def cached_thumb(instance):
    if not instance.image:
        return
    cached = ImageCacheFile(AdminThumbnailSpec(instance.image))
    cached.generate()
    return cached


@admin.register(SpeciesName)
class SpeciesNameAdmin(admin.ModelAdmin):
    list_filter = ['language']
    list_display = ['name', 'language', 'species_link']
    list_display_links = ['name']
    search_fields = ['name', 'species__sciname', 'species__gername', 'species__engname']
    autocomplete_fields = ['species']

    @admin.display(
        description="Species",
        ordering='species__sciname'
    )
    def species_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:species_species_change", args=[obj.species.id]),
            str(obj.species)
        )


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1

    verbose_name_plural = "Additional names"


class YesNoFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return [
            ("y", "Yes"),
            ("n", "No"),
        ]


class HasGbifusagekeyFilter(YesNoFilter):
    title = "gbifusagekey"
    parameter_name = "has_gbifusagekey"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                gbifusagekey__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                gbifusagekey__isnull=True
            )


class PortraitIsSynonymFilter(YesNoFilter):
    title = "portrait is synonym"
    parameter_name = "portrait_is_synonym"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                species__accepted_species__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                species__accepted_species__isnull=True
            )


class IsSynonymFilter(YesNoFilter):
    title = "is synonym"
    parameter_name = "is_synonym"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                accepted_species__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                accepted_species__isnull=True
            )


class HasSynonymsFilter(YesNoFilter):
    title = "has synonyms"
    parameter_name = "has_synonyms"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                species__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                species__isnull=True
            )


class HasAvatarFilter(YesNoFilter):
    title = "avatar"
    parameter_name = "has_avatar"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                avatar__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                avatar__isnull=True
            )


class HasFemaleAvatarFilter(YesNoFilter):
    title = "female avatar"
    parameter_name = "has_female_avatar"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                female_avatar__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                female_avatar__isnull=True
            )


class HasPrimaryName(admin.SimpleListFilter):
    title = "primary name"
    parameter_name = "has_primary_name"

    def lookups(self, request, model_admin):
        return [
            ("g", "German"),
            ("e", "English"),
            ("b", "Both"),
            ("i", "Either"),
            ("n", "None")
        ]

    def queryset(self, request, queryset):
        if self.value() == "g":
            return queryset.filter(
                gername__isnull=False
            )
        if self.value() == "e":
            return queryset.filter(
                engname__isnull=False
            )
        if self.value() == "b":
            return queryset.filter(
                engname__isnull=False,
                gername__isnull=False
            )
        if self.value() == "i":
            return queryset.filter(
                models.Q(engname__isnull=False) | models.Q(gername__isnull=False)
            )
        if self.value() == "n":
            return queryset.filter(
                engname__isnull=True,
                gername__isnull=True
            )


class HasAdditionalNames(YesNoFilter):
    title = "additional names"
    parameter_name = "has_additional_names"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                speciesname__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                speciesname__isnull=True
            )


class HasPlantnetPowoidFilter(YesNoFilter):
    title = "plantnetpowoid"
    parameter_name = "has_plantnetpowoid"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                plantnetpowoid__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                plantnetpowoid__isnull=True
            )


class HasPlantnetPowoidMappingFilter(YesNoFilter):
    title = "plantnet mapping"
    parameter_name = "has_plantnetpowoid_mapping"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                plantnetpowoidmapping__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                plantnetpowoidmapping__isnull=True
            )


class HasNbclassidFilter(YesNoFilter):
    title = "nbclassid"
    parameter_name = "has_nbclassid"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                nbclassid__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                nbclassid__isnull=True
            )


class HasPortraitFilter(YesNoFilter):
    title = "portrait"
    parameter_name = "has_portrait"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(portrait__isnull=False)
        if self.value() == "n":
            return queryset.filter(portrait__isnull=True)


class HasWikipediaFilter(YesNoFilter):
    title = "wikipedia"
    parameter_name = "has_wikipedia"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                wikipedia__isnull=False
            )
        if self.value() == "n":
            return queryset.filter(
                wikipedia__isnull=True
            )


class ImportAvatarFromWikimediaForm(forms.Form):
    wikimedia_url = forms.URLField(label="Wikimedia image URL")


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ["species/admin.css"],
        }

    inlines = [
        SpeciesNameInline
    ]
    readonly_fields = ['speciesid']
    list_display = ['id', 'speciesid', 'sciname', 'gername', 'avatar_crop', 'accepted', 'portrait', 'gbif', 'plantnet',
                    'search']
    list_display_links = ['id', 'speciesid']
    list_filter = ['group__nature', HasPortraitFilter, HasGbifusagekeyFilter, HasPrimaryName, HasSynonymsFilter,
                   IsSynonymFilter, HasPlantnetPowoidFilter, HasPlantnetPowoidMappingFilter, HasNbclassidFilter,
                   'autoid', HasAvatarFilter, HasFemaleAvatarFilter, HasAdditionalNames, HasWikipediaFilter, 'group']
    search_fields = ['id', 'speciesid', 'sciname', 'gername', 'gbifusagekey']
    fields = ['speciesid',
              'group',
              'gername',
              'sciname',
              'engname',
              'wikipedia',
              'autoid',
              'nbclassid',
              ('red_list_germany',
               'iucncategory'),
              ('activity_start_month',
               'activity_end_month'),
              ('activity_start_hour',
               'activity_end_hour'),
              'avatar',
              'female_avatar',
              'gbifusagekey',
              'accepted_species',
              'plantnetpowoid',
              'tag',
              ]

    raw_id_fields = ['accepted_species']
    ordering = ('sciname',)
    filter_horizontal = ['tag']
    autocomplete_fields = ['avatar', 'female_avatar']
    actions = ['make_autoid_enabled', 'import_avatar_from_wikimedia']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.view_name.endswith('changelist'):
            return qs.select_related('avatar', 'group').prefetch_related('portrait_set')
        return qs

    @admin.action(description="Mark selected species as available for autoid")
    def make_autoid_enabled(self, request, queryset):
        updated = queryset.update(autoid=True)
        self.message_user(
            request,
            ngettext(
                "%d species was successfully marked as available for autoid.",
                "%d species were successfully marked as available for autoid.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Import avatar from Wikimedia")
    @transaction.atomic
    def import_avatar_from_wikimedia(self, request, queryset):
        if request.POST.get("post"):
            form = ImportAvatarFromWikimediaForm(request.POST)
            if form.is_valid():
                meta = utils.get_metadata(form.cleaned_data['wikimedia_url'])
                avatar = Avatar.objects.create(owner=meta.author, owner_link=meta.author_url, source=meta.image_url,
                                               license=meta.license, image=meta.image)
                queryset.update(avatar=avatar.id)
                return HttpResponseRedirect(reverse('admin:species_avatar_change', args=(avatar.id,)))
        else:
            form = ImportAvatarFromWikimediaForm()

        return TemplateResponse(request, 'admin/avatar_from_wikimedia.html', {"form": form, 'queryset': queryset})

    @admin.display(
        description="Avatar"
    )
    def avatar_crop(self, obj):
        avatar = obj.avatar
        if avatar:
            image_url = get_backend().get_thumbnail_url(
                avatar.image,
                {
                    'size': (400, 400),
                    'box': avatar.cropping,
                    'crop': True,
                    'detail': True,
                }
            )
            url = reverse('admin:species_avatar_change', args=(avatar.id,))
            return format_html('<a href="{}"><img src="{}" class="species-avatar"/></a>', url, image_url)
        else:
            return "-"

    @admin.display(
        description='Search'
    )
    def search(self, obj):
        plantnet_url = f'https://identify.plantnet.org/k-world-flora/species?search={obj.sciname}'
        plantnet_img_url = static('species/plantnet_white_border_marker.png')
        gbif_url = f'https://www.gbif.org/species/search?q={obj.sciname}'
        gbif_img_url = static('species/gbif-mark-green-logo.png')
        scientific_url_name = obj.sciname.replace(' ', '_')
        wikipedia_url = f'https://en.wikipedia.org/wiki/{scientific_url_name}'
        wikipedia_img_url = static('species/Wikipedia-logo-v2.svg')
        scientific_wikimedia_url_name = obj.sciname.replace(' ', '+')
        wikimedia_url = f'https://commons.wikimedia.org/w/index.php?search={scientific_wikimedia_url_name}&title=Special:MediaSearch&type=image'
        wikimedia_img_url = static('species/Wikimedia Commons Logo.svg')
        return format_html(
            '<a title="GBIF" href="{}"><img class="image-link" src={}></a> | <a title="Wikipedia" href="{}"><img class="image-link" src={}></a> | <a href="{}"><img title="Wikimedia Image Search" class="image-link" src={}></a> | <a title="Plantnet" href="{}"><img class="image-link" src={}></a>',
            gbif_url, gbif_img_url, wikipedia_url, wikipedia_img_url, wikimedia_url, wikimedia_img_url, plantnet_url,
            plantnet_img_url)

    @admin.display(
        description='Powo ID (Plantnet)'
    )
    def plantnet(self, obj):
        if obj.plantnetpowoid is None:
            return '-'
        else:
            plantnet_url = f'https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:{obj.plantnetpowoid}'
            return format_html(f'<a href="{{}}">{obj.plantnetpowoid}</a>', plantnet_url)

    @admin.display()
    def gbif(self, obj):
        if obj.gbifusagekey is None:
            return '-'
        else:
            gbif_url = f'https://www.gbif.org/species/{obj.gbifusagekey}'
            return format_html(f'<a href="{{}}">{obj.gbifusagekey}</a>', gbif_url)

    @admin.display(description='Synonym of')
    def accepted(self, obj):
        if obj.accepted_species is None:
            return "-"
        else:
            url = reverse('admin:species_species_change', args=(obj.accepted_species.id,))
            return format_html(f'<a href="{{}}">{obj.accepted_species.sciname}</a>', url)

    @admin.display()
    def portrait(self, obj):
        if obj.group.nature is None or obj.accepted_species:
            return "-"
        else:
            links = []
            urls = []

            for lang in ['de', 'en']:
                portrait = [portrait for portrait in obj.portrait_set.all() if portrait.language == lang]
                if portrait:
                    url = reverse(f'admin:species_{obj.group.nature}portrait_change', args=(portrait[0].id,))
                    links.append(f'<a href="{{}}" class="changelink">{lang}</a>')
                    urls.append(url)
                else:
                    url = reverse(f'admin:species_{obj.group.nature}portrait_add')
                    links.append(f'<a href="{{}}"  class="addlink">{lang}</a>')
                    urls.append(f'{url}?species={obj.id}&language={lang}')

            links.append('<a href="{}"><img class="naturblick-logo-link" src="{}"/></a>')
            return format_html(' | '.join(links), urls[0], urls[1], f'/species/portrait/{obj.id}',
                               static('species/logo.svg'))


#
# Portrait
#
class SourceInlineFormSet(BaseInlineFormSet):
    class Meta:
        model = Source
        fields = '__all__'


class SourceInline(OrderableAdmin, admin.TabularInline):
    model = Source
    formset = SourceInlineFormSet
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class GoodToKnowInline(OrderableAdmin, admin.TabularInline):
    model = GoodToKnow
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class SimilarSpeciesInline(OrderableAdmin, admin.TabularInline):
    model = SimilarSpecies
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }
    autocomplete_fields = ['species']


class AdditionalLinkInline(OrderableAdmin, admin.TabularInline):
    model = AdditionalLink
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class UnambigousFeatureInline(OrderableAdmin, admin.TabularInline):
    model = UnambigousFeature
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


@admin.register(PortraitImageFile)
class PortraitImageFileAdmin(admin.ModelAdmin):
    search_fields = ['owner', 'image', 'species__sciname', 'species__gername', 'species__speciesid']
    fields = ['image', 'admin_thumbnail', 'species', 'owner', 'owner_link', 'source', 'license', 'width', 'height']
    readonly_fields = ['admin_thumbnail', 'width', 'height']
    list_display = ['id', 'admin_thumbnail', 'image']
    list_display_links = ['id', 'admin_thumbnail']
    autocomplete_fields = ['species']

    admin_thumbnail = AdminThumbnail(image_field=cached_thumb)
    admin_thumbnail.short_description = 'Image'


class DescMetaInline(admin.StackedInline):
    extra = 0
    model = DescMeta
    autocomplete_fields = ['portrait_image_file']
    verbose_name = 'Description image'


class FunFactMetaInline(admin.StackedInline):
    model = FunFactMeta
    extra = 0
    autocomplete_fields = ['portrait_image_file']
    verbose_name = 'Funfact image'


class InTheCityMetaInline(admin.StackedInline):
    model = InTheCityMeta
    extra = 0
    autocomplete_fields = ['portrait_image_file']
    verbose_name = 'In the city image'


@admin.action(description="Copy selected portrait to english")
@transaction.atomic
def copy_portrait_to_eng(modeladmin, request, queryset):
    def copy_ref(ref, new_portrait):
        ref.id = None
        ref._state.adding = True
        ref.portrait = new_portrait
        ref.save()

    is_fauna_portrait = isinstance(modeladmin, FaunaportraitAdmin)
    if is_fauna_portrait:
        model = Faunaportrait
    else:
        model = Floraportrait

    if queryset.filter(~Q(language='de')).exists():
        messages.error(request, "Please select only german portraits.")
        return
    if model.objects.filter(
            Q(species_id__in=queryset.values_list('species__id', flat=True)) & Q(language='en')).exists():
        messages.error(request, "At least one english portrait for the selected species already exists.")
        return

    for p in queryset:
        if is_fauna_portrait:
            new_portrait = Faunaportrait(
                species=p.species,
                language='en',
                short_description=p.short_description,
                city_habitat=p.city_habitat,
                human_interaction=p.human_interaction,
                published=False,
                male_description=p.male_description,
                female_description=p.female_description,
                juvenile_description=p.juvenile_description,
                tracks=p.tracks,
                audio_title=p.audio_title,
                faunaportrait_audio_file=p.faunaportrait_audio_file)
        else:
            new_portrait = Floraportrait(species=p.species,
                                         language='en',
                                         short_description=p.short_description,
                                         city_habitat=p.city_habitat,
                                         human_interaction=p.human_interaction,
                                         published=False,
                                         leaf_description=p.leaf_description,
                                         stem_axis_description=p.stem_axis_description,
                                         flower_description=p.flower_description,
                                         fruit_description=p.fruit_description)
        new_portrait.save()

        if hasattr(p, 'descmeta'):
            copy_ref(p.descmeta, new_portrait)

        if hasattr(p, 'inthecitymeta'):
            copy_ref(p.inthecitymeta, new_portrait)

        if hasattr(p, 'funfactmeta'):
            copy_ref(p.funfactmeta, new_portrait)

        if hasattr(p, 'goodtoknow_set'):
            for goodtoknow in p.goodtoknow_set.all():
                copy_ref(goodtoknow, new_portrait)

        if hasattr(p, 'source_set'):
            for source in p.source_set.all():
                copy_ref(source, new_portrait)

        if hasattr(p, 'similarspecies_set'):
            for similarspecies in p.similarspecies_set.all():
                copy_ref(similarspecies, new_portrait)

        if hasattr(p, 'unambigousfeature_set'):
            for unambigousfeature in p.unambigousfeature_set.all():
                copy_ref(unambigousfeature, new_portrait)

        if hasattr(p, 'additionallink_set'):
            for additionallink in p.additionallink_set.all():
                copy_ref(additionallink, new_portrait)


@admin.action(description="Move selected portrait to accepted species")
def move_portrait_to_accepted(modeladmin, request, queryset):
    def move_portrait_image_file(meta, accepted_species):
        if meta:
            portrait_image_file = meta.portrait_image_file
            if portrait_image_file:
                portrait_image_file.species = accepted_species
                portrait_image_file.save()

    # check correct selection
    if queryset.filter(species__accepted_species__isnull=True).exists():
        modeladmin.message_user(
            request,
            "Not all selected portraits have an accepted species - use filter 'portrait is synonym species'.",
            level=messages.WARNING
        )
        return

    for portrait in queryset:
        all_lang_portrait_ids = Portrait.objects.filter(species=portrait.species).values_list('id', flat=True)
        qs_portrait_ids = queryset.values_list('id', flat=True)
        if not all(p in qs_portrait_ids for p in all_lang_portrait_ids):
            modeladmin.message_user(
                request,
                "You have to select all portraits of a specific species'.",
                level=messages.WARNING
            )
            return

    # update data
    with transaction.atomic():
        for portrait in queryset.select_related('species__accepted_species'):
            accepted_species = portrait.species.accepted_species
            if accepted_species:
                # move avatars
                synonym_species = portrait.species
                if synonym_species.avatar and not accepted_species.avatar:
                    accepted_species.avatar = synonym_species.avatar
                    accepted_species.save()
                if synonym_species.female_avatar and not accepted_species.female_avatar:
                    accepted_species.female_avatar = synonym_species.female_avatar
                    accepted_species.save()

                # remove accepted species from similar species
                portrait.similarspecies_set.filter(species_id=accepted_species.id).delete()

                # move species
                portrait.species = accepted_species
                portrait.save()

                # move portrait image files
                move_portrait_image_file(getattr(portrait, 'descmeta', None), accepted_species)
                move_portrait_image_file(getattr(portrait, 'funfactmeta', None), accepted_species)
                move_portrait_image_file(getattr(portrait, 'inthecitymeta', None), accepted_species)


def portrait_fieldorder(fields):
    fields.remove('published')
    fields.remove('species')
    fields.insert(0, ('species', 'published'))
    fields.remove('city_habitat')
    fields.remove('human_interaction')
    fields.remove('ecosystem_role')
    fields.append('city_habitat')
    fields.append('human_interaction')
    fields.append('ecosystem_role')
    return fields


@admin.register(Floraportrait)
class FloraportraitAdmin(admin.ModelAdmin):
    list_display = ['id', 'species__speciesid', 'species__sciname', 'species__gername', 'published', 'language']
    search_fields = ('id', 'species__speciesid', 'species__sciname', 'species__gername')
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published', 'language', PortraitIsSynonymFilter, 'species__group')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline,
        DescMetaInline, InTheCityMetaInline, FunFactMetaInline
    ]
    ordering = ('species__sciname',)
    autocomplete_fields = ['species']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})}
    }
    actions = [move_portrait_to_accepted, copy_portrait_to_eng]

    def get_fields(self, request, obj=None, **kwargs):
        return portrait_fieldorder(super().get_fields(request, obj, **kwargs))


@admin.register(FaunaportraitAudioFile)
class FaunaportraitAudioFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'audio_file', 'species__gername', 'species__sciname']
    search_fields = ['owner', 'audio_file']
    fields = ['audio_file',
              'species',
              'owner',
              'owner_link',
              'source',
              'license'
              ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['species'].queryset = Species.objects.filter(group__nature='fauna')
        return form


@admin.register(Faunaportrait)
class FaunaportraitAdmin(admin.ModelAdmin):
    list_display = ['id', 'species__speciesid', 'species__sciname', 'species__gername', 'published', 'language']
    search_fields = ('id', 'species__speciesid', 'species__sciname', 'species__gername')
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published', 'language', PortraitIsSynonymFilter, 'species__group')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline,
        DescMetaInline, InTheCityMetaInline, FunFactMetaInline
    ]
    ordering = ["species__sciname"]
    autocomplete_fields = ['species', 'faunaportrait_audio_file']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})}
    }
    actions = [move_portrait_to_accepted, copy_portrait_to_eng]

    def get_fields(self, request, obj=None, **kwargs):
        return portrait_fieldorder(super().get_fields(request, obj, **kwargs))


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    radio_fields = {"nature": admin.VERTICAL}
    list_display = ['name', 'nature', 'admin_thumbnail', 'svg_preview', 'has_portraits', 'is_fieldbookfilter',
                    'has_characters']
    list_filter = ['nature']
    fields = ['name', 'nature', 'image', 'admin_thumbnail', 'svg', 'svg_preview', 'gername', 'engname', 'has_portraits',
              'is_fieldbookfilter', 'has_characters']
    readonly_fields = ['admin_thumbnail', 'svg_preview']

    admin_thumbnail = AdminThumbnail(image_field=cached_thumb)
    admin_thumbnail.short_description = 'Image'

    def svg_preview(self, obj):
        if obj.svg and obj.svg.name.endswith('.svg'):
            return format_html('<img src="{}" alt="icon" height="50" width="50" />', obj.svg.url)
        return "N/A"

    svg_preview.short_description = "SVG"


class HasSpecies(YesNoFilter):
    title = "species"
    parameter_name = "has_species"

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(
                Q(avatar_species__isnull=False) | Q(female_avatar_species__isnull=False)
            )
        if self.value() == "n":
            return queryset.filter(
                Q(avatar_species__isnull=True) & Q(female_avatar_species__isnull=True)
            )


@admin.register(Avatar)
class AvatarAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['id', 'cropped_image', 'image', 'owner', 'species_list']
    list_filter = [HasSpecies]
    search_fields = ['image', 'owner', 'avatar_species__sciname', 'avatar_species__gername',
                     'avatar_species__speciesid', 'female_avatar_species__sciname', 'female_avatar_species__gername',
                     'female_avatar_species__speciesid']
    fields = ['cropping', 'image', 'owner', 'owner_link', 'source', 'license']

    @admin.display(
        description="Cropped Image"
    )
    def cropped_image(self, obj):
        image_url = get_backend().get_thumbnail_url(
            obj.image,
            {
                'size': (400, 400),
                'box': obj.cropping,
                'crop': True,
                'detail': True,
            }
        )
        return mark_safe(f'<img src="{image_url}" width="100" height="100" />')

    @admin.display(
        description="Species"
    )
    def species_list(self, obj):
        return format_html_join(
            ', ',
            '<a href="{}">{}</a>',
            ((reverse("admin:species_species_change", args=[species.id]), str(species))
             for species in obj.avatar_species.all())
        )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("avatar_species")


@admin.register(SourcesImprint)
class SourcesImprintAdmin(admin.ModelAdmin):
    list_filter = ['name']
    ordering = ['scie_name']
    search_fields = ['scie_name']


@admin.register(SourcesTranslation)
class SourcesTranslationAdmin(admin.ModelAdmin):
    list_filter = ['key', 'language']
    ordering = ['value']
    search_fields = ['key', 'value']
    list_display = ['key', 'value', 'language']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name', 'english_name']
    list_display = ['name', 'english_name']


@admin.register(PlantnetPowoidMapping)
class PlantnetPowoidMappingAdmin(admin.ModelAdmin):
    list_display = ['plantnetpowoid', 'species']
    autocomplete_fields = ['species_plantnetpowoid']

    @admin.display(description="Species plantnetpowoid")
    def species(self, obj):
        link = reverse("admin:species_species_change", args=[obj.species_plantnetpowoid.id])
        return format_html('<a href="{}">{} ({})</a>', link, obj.species_plantnetpowoid.plantnetpowoid,
                           obj.species_plantnetpowoid)


class LeichtRecognizeInline(OrderableAdmin, admin.TabularInline):
    extra = 0
    model = LeichtRecognize
    verbose_name = 'Leicht recognize text'
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 60})}
    }
    ordering_field_hide_input = True

class LeichtGoodtoknowInline(OrderableAdmin, admin.TabularInline):
    extra = 0
    model = LeichtGoodToKnow
    verbose_name = 'Leicht goodtoknow text'
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 60})}
    }
    ordering_field_hide_input = True

class LeichtPortraitAdminForm(forms.ModelForm):
    class Meta:
        model = LeichtPortrait
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        species = cleaned_data.get("species")
        recognize_image = cleaned_data.get("recognize_image")
        goodtoknow_image = cleaned_data.get("goodtoknow_image")

        if recognize_image and recognize_image.species != species:
            raise ValidationError({
                "recognize_image": "Recognize image must have the same species as the portrait."
            })

        if goodtoknow_image and goodtoknow_image.species != species:
            raise ValidationError({
                "goodtoknow_image": "Good-to-know image must have the same species as the portrait."
            })

        return cleaned_data


@admin.register(LeichtPortrait)
class LeichtPortraitAdmin(admin.ModelAdmin):
    form = LeichtPortraitAdminForm
    list_display = ['species__speciesid', 'species__sciname', 'species__gername']
    search_fields = ['species__speciesid', 'species__sciname', 'species__gername']
    search_help_text = 'Sucht über alle Artnamen'
    ordering = ["species__sciname"]
    autocomplete_fields = ['species', 'recognize_image', 'goodtoknow_image']
    inlines = [LeichtRecognizeInline, LeichtGoodtoknowInline]
