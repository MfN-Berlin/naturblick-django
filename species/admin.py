import logging

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from image_cropping import ImageCroppingMixin

from .models import Species, SpeciesName, Source, GoodToKnow, SimilarSpecies, AdditionalLink, UnambigousFeature, \
    AudioFile, PortraitImageFile, DescMeta, FunFactMeta, InTheCityMeta, Faunaportrait, Avatar, Group, Floraportrait, \
    Tag, Character, CharacterValue, SourcesImprint, SourcesTranslation

logger = logging.getLogger(__name__)


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1


class PortraitImageFileInline(admin.TabularInline):
    model = PortraitImageFile
    extra = 0


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline, PortraitImageFileInline
    ]
    readonly_fields = ['speciesid']
    list_display = ['speciesid', 'group', 'gername', 'sciname', 'portrait']
    list_filter = ('group__nature', 'group')
    search_fields = ['gername', 'sciname', 'speciesid']
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
              'accepted_id',
              ]
    ordering = ('gername',)

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


class GoodToKnowInline(admin.TabularInline):
    model = GoodToKnow
    extra = 0


class SimilarSpeciesInline(admin.TabularInline):
    model = SimilarSpecies
    extra = 0


class AdditionalLinkInline(admin.TabularInline):
    model = AdditionalLink
    extra = 0


class UnambigousFeatureInline(admin.TabularInline):
    model = UnambigousFeature
    extra = 0


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(PortraitImageFile)
class PortraitImageFileAdmin(admin.ModelAdmin):
    search_fields = ['owner', 'image']


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
    list_display = ['species__speciesid', 'species__group', 'species__gername', 'language']
    search_fields = ('species__species_names__name',)
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published', 'language')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline,
        DescMetaInline, FunFactMetaInline, InTheCityMetaInline
    ]
    ordering = ('species__gername',)
    autocomplete_fields = ['species']


@admin.register(Faunaportrait)
class FaunaportraitAdmin(admin.ModelAdmin):
    list_display = ['species__speciesid', 'species__group', 'species__gername', 'language', 'audiofile']
    search_fields = ('species__species_names__name', 'species__gername',)
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published', 'language')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline,
        DescMetaInline, FunFactMetaInline, InTheCityMetaInline
    ]
    ordering = ["species__gername"]
    autocomplete_fields = ['species']

    def audiofile(self, obj):
        if hasattr(obj.species, 'audio_file'):
            url = reverse(f'admin:species_audiofile_change', args=(obj.species.audio_file.id,))
            link = f'<a href="{{}}" class="changelink"></a>'
            return format_html(link, url)
        else:
            url = reverse(f'admin:species_audiofile_add') + f'?species={obj.species.id}'
            link = f'<a href="{{}}"  class="addlink"></a>'
            return format_html(link, url)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    radio_fields = {"nature": admin.VERTICAL}
    list_display = ['name', 'nature']
    list_filter = ['nature']


@admin.register(Avatar)
class AvatarAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['image_tag', 'image', 'owner']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image.url))

class CharacterValueInline(admin.TabularInline):
    model = CharacterValue
    extra = 0

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    inlines = [ CharacterValueInline ]

@admin.register(SourcesImprint)
class SourcesImprintAdmin(admin.ModelAdmin):
    pass

@admin.register(SourcesTranslation)
class SourcesTranslationAdmin(admin.ModelAdmin):
    pass

# class Tag(models.Model):