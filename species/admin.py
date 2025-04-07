import logging

from django import forms
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.forms.models import BaseInlineFormSet
from django.urls import reverse
from django.utils.html import format_html
from image_cropping import ImageCroppingMixin
from imagekit import ImageSpec
from imagekit.admin import AdminThumbnail
from imagekit.cachefiles import ImageCacheFile
from imagekit.processors import ResizeToFit

from .models import Species, SpeciesName, Source, GoodToKnow, SimilarSpecies, AdditionalLink, UnambigousFeature, \
    PortraitImageFile, DescMeta, FunFactMeta, InTheCityMeta, Faunaportrait, Avatar, Group, Floraportrait, \
    Tag, Character, CharacterValue, SourcesImprint, SourcesTranslation, FaunaportraitAudioFile

logger = logging.getLogger(__name__)


class AdminThumbnailSpec(ImageSpec):
    processors = [ResizeToFit(150, None)]
    format = 'JPEG'
    options = {'quality': 60}


def cached_thumb(instance):
    cached = ImageCacheFile(AdminThumbnailSpec(instance.image))
    cached.generate()
    return cached


def validate_order(theforms, name):
    order_numbers = set()
    for form in theforms:
        if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
            order_number = form.cleaned_data.get('order')
            if order_number in order_numbers:
                raise forms.ValidationError(f"Two {name} could not have same order.")
            order_numbers.add(order_number)

    for i, _ in enumerate(order_numbers):
        if i + 1 not in order_numbers:
            raise forms.ValidationError(
                f"The order numbers of {name} must be consecutive numbers from 1 up to {len(order_numbers)} (in any order)")


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1

    verbose_name_plural = "Additional names"


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline
    ]
    readonly_fields = ['speciesid']
    list_display = ['id', 'speciesid', 'sciname', 'gername', 'portrait']
    list_display_links = ['id', 'speciesid']
    list_filter = ('group__nature', 'group')
    search_fields = ['id', 'speciesid', 'sciname', 'gername']
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
              'tag'
              ]

    raw_id_fields = ['accepted_species']
    ordering = ('sciname',)
    filter_horizontal = ['tag']
    autocomplete_fields = ['avatar', 'female_avatar']

    def portrait(self, obj):
        if obj.group.nature is None:
            return "-"
        else:
            links = []
            urls = []
            for lang in ['de', 'en']:
                portrait = obj.portrait_set.filter(language=lang)

                if portrait.exists():
                    url = reverse(f'admin:species_{obj.group.nature}portrait_change', args=(portrait.first().id,))
                    links.append(f'<a href="{{}}" class="changelink">{lang}</a>')
                    urls.append(url)
                else:
                    url = reverse(f'admin:species_{obj.group.nature}portrait_add')
                    links.append(f'<a href="{{}}"  class="addlink">{lang}</a>')
                    urls.append(f'{url}?species={obj.id}&language={lang}')

            return format_html(' | '.join(links), urls[0], urls[1])


#
# Portrait
#
class SourceInlineFormSet(BaseInlineFormSet):
    class Meta:
        model = Source
        fields = '__all__'

    def clean(self):
        super().clean()
        validate_order(self.forms, "Source")


class SourceInline(admin.TabularInline):
    model = Source
    formset = SourceInlineFormSet
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class GoodToKnowInlineFormSet(BaseInlineFormSet):
    class Meta:
        model = GoodToKnow
        fields = '__all__'

    def clean(self):
        super().clean()
        validate_order(self.forms, "GoodToKnow")


class GoodToKnowInline(admin.TabularInline):
    model = GoodToKnow
    formset = GoodToKnowInlineFormSet
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class SimilarSpeciesFormSet(BaseInlineFormSet):
    class Meta:
        model = SimilarSpecies
        fields = '__all__'

    def clean(self):
        super().clean()
        validate_order(self.forms, "SimilarSpecies")


class SimilarSpeciesInline(admin.TabularInline):
    model = SimilarSpecies
    formset = SimilarSpeciesFormSet
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }
    autocomplete_fields = ['species']


class AdditionalLinkFormSet(BaseInlineFormSet):
    class Meta:
        model = AdditionalLink
        fields = '__all__'

    def clean(self):
        super().clean()
        validate_order(self.forms, "AdditionalLink")


class AdditionalLinkInline(admin.TabularInline):
    model = AdditionalLink
    formset = AdditionalLinkFormSet
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class UnambigousFeatureFormSet(BaseInlineFormSet):
    class Meta:
        model = UnambigousFeature
        fields = '__all__'

    def clean(self):
        super().clean()
        validate_order(self.forms, "AdditionalLink")


class UnambigousFeatureInline(admin.TabularInline):
    model = UnambigousFeature
    formset = UnambigousFeatureFormSet
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


@admin.register(Floraportrait)
class FloraportraitAdmin(admin.ModelAdmin):
    list_display = ['id', 'species__speciesid', 'species__sciname', 'species__gername', 'published', 'language']
    search_fields = ('id', 'species__speciesid', 'species__sciname', 'species__gername')
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published', 'language')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline,
        DescMetaInline, FunFactMetaInline, InTheCityMetaInline
    ]
    ordering = ('species__sciname',)
    autocomplete_fields = ['species']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})}
    }

    def get_fields(self, request, obj=None, **kwargs):
        fields = super().get_fields(request, obj, **kwargs)
        fields.remove('published')
        fields.remove('species')
        fields.insert(0, ('species', 'published'))
        return fields


@admin.register(FaunaportraitAudioFile)
class FaunaportraitAudioFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'audio_file', 'species__gername', 'species__sciname']
    search_fields = ['owner', 'audio_file', 'audio_spectrogram']
    fields = ['audio_file',
              'audio_spectrogram',
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
    list_filter = ('published', 'language')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline,
        DescMetaInline, FunFactMetaInline, InTheCityMetaInline
    ]
    ordering = ["species__sciname"]
    autocomplete_fields = ['species', 'faunaportrait_audio_file']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})}
    }

    def get_fields(self, request, obj=None, **kwargs):
        fields = super().get_fields(request, obj, **kwargs)
        fields.remove('published')
        fields.remove('species')
        fields.insert(0, ('species', 'published'))
        return fields


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    radio_fields = {"nature": admin.VERTICAL}
    list_display = ['name', 'nature']
    list_filter = ['nature']


@admin.register(Avatar)
class AvatarAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['id', 'avatar_thumbnail', 'image', 'owner']
    search_fields = ['image', 'owner']
    fields = ['avatar_thumbnail', 'image', 'owner', 'owner_link', 'source', 'license', 'cropping']
    readonly_fields = ['avatar_thumbnail']

    avatar_thumbnail = AdminThumbnail(image_field=cached_thumb)
    avatar_thumbnail.short_description = 'Image'


@admin.register(CharacterValue)
class CharacterValueAdmin(admin.ModelAdmin):
    fields = ['character', 'gername', 'engname', 'colors', 'dots', 'image', 'thumbnail']
    list_display = ['character', 'thumbnail', 'gername', 'engname']
    list_display_links = ['character', 'thumbnail']
    readonly_fields = ['thumbnail']

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:100px; max-height:100px"/>'.format(obj.image.url))
        else:
            return "-"

    thumbnail.short_description = 'Image'


class CharacterValueInline(admin.TabularInline):
    model = CharacterValue
    extra = 0


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    inlines = [CharacterValueInline]
    list_display = ['gername', 'engname', 'group']
    list_filter = ['group']
    ordering = ['gername']
    search_fields = ['gername']
    fields = [('gername', 'engname'), 'group', 'display_name', 'weight', 'single_choice',
              ('gerdescription', 'engdescription')]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 40})}
    }


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
