import logging

from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html
from image_cropping import ImageCroppingMixin

from .models import Species, SpeciesName, Source, GoodToKnow, SimilarSpecies, AdditionalLink, UnambigousFeature, \
    PortraitImageFile, DescMeta, FunFactMeta, InTheCityMeta, Faunaportrait, Avatar, Group, Floraportrait, \
    Tag, Character, CharacterValue, SourcesImprint, SourcesTranslation, FaunaportraitAudioFile

logger = logging.getLogger(__name__)


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1


class PortraitImageFileInline(admin.TabularInline):
    model = PortraitImageFile
    extra = 0


class FaunaportraitAudioFileInline(admin.TabularInline):
    model = FaunaportraitAudioFile
    extra = 0


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline, PortraitImageFileInline, FaunaportraitAudioFileInline
    ]
    readonly_fields = ['speciesid']
    list_display = ['id', 'speciesid', 'sciname', 'gername', 'portrait']
    list_filter = ('group__nature', 'group')
    search_fields = ['id', 'speciesid', 'sciname', 'gername']
    fields = ['speciesid',
              'group',
              'gername',
              'sciname',
              'engname',
              'wikipedia',
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
    ordering = ('gername',)
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
class SourceInline(admin.TabularInline):
    model = Source
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class GoodToKnowInline(admin.TabularInline):
    model = GoodToKnow
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class SimilarSpeciesInline(admin.TabularInline):
    model = SimilarSpecies
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class AdditionalLinkInline(admin.TabularInline):
    model = AdditionalLink
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


class UnambigousFeatureInline(admin.TabularInline):
    model = UnambigousFeature
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})}
    }


@admin.register(PortraitImageFile)
class PortraitImageFileAdmin(admin.ModelAdmin):
    search_fields = ['owner', 'image']
    fields = ['species', 'image_tag', 'image', 'owner', 'owner_link', 'source', 'license']
    readonly_fields = ['image_tag']
    list_display = ['id', 'image_tag', 'image']
    autocomplete_fields = ['species']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:100px; max-height:100px"/>'.format(obj.image.url))

    image_tag.short_description = 'Image'


class DescMetaInline(admin.StackedInline):
    extra = 0
    model = DescMeta
    autocomplete_fields = ['portrait_image_file']


class FunFactMetaInline(admin.StackedInline):
    model = FunFactMeta
    extra = 0
    autocomplete_fields = ['portrait_image_file']


class InTheCityMetaInline(admin.StackedInline):
    model = InTheCityMeta
    extra = 0
    autocomplete_fields = ['portrait_image_file']


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
    ordering = ('species__speciesid',)
    autocomplete_fields = ['species']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})}
    }


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
    ordering = ["species__speciesid"]
    autocomplete_fields = ['species']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})}
    }


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    radio_fields = {"nature": admin.VERTICAL}
    list_display = ['name', 'nature']
    list_filter = ['nature']


@admin.register(Avatar)
class AvatarAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['id', 'list_thumbnail', 'image', 'owner']
    search_fields = ['image', 'owner']
    fields = ['thumbnail', 'image', 'owner', 'owner_link', 'source', 'license', 'cropping']
    readonly_fields = ['thumbnail']

    def list_thumbnail(self, obj):
        return format_html('<img src="{}" style="max-width:100px; max-height:100px"/>'.format(obj.image.url))


@admin.register(CharacterValue)
class CharacterValueAdmin(admin.ModelAdmin):
    fields = ['character', 'gername', 'engname', 'colors', 'dots', 'image', 'thumbnail']
    list_display = ['character', 'gername', 'engname']
    readonly_fields = ['thumbnail']

    def thumbnail       (self, obj):
        return format_html('<img src="{}" style="max-width:100px; max-height:100px"/>'.format(obj.image.url))

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
