from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from image_cropping import ImageCroppingMixin
from reportlab.lib.pagesizes import portrait

from .models import Species, Group, Floraportrait, Faunaportrait, SpeciesName, Source, GoodToKnow, Avatar, \
    SimilarSpecies, AdditionalLink, UnambigousFeature, DescriptionImage, Portrait


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline
    ]
    readonly_fields = ['speciesid']
    list_display = ['speciesid', 'group', 'gername', 'sciname', 'portrait']
    list_filter = ('group__nature', 'group')
    search_fields = ["species_names__name", 'gername']
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
              'accepted',
              ]
    ordering = ('gername',)

    def portrait(self, obj):
        if obj.group.nature is None:
            return "-"
        else:
            links = []
            urls = []
            for lang in ['de', 'en']:
                portrait = obj.portrait.filter(language=lang)

                if portrait.exists():
                    url = reverse(f'admin:species_{obj.group.nature}portrait_change', args=(portrait.first().id,))
                    links.append(f'<a href="{{}}">{lang}</a>')
                    urls.append(url)
                else:
                    url_with_params = f"reverse(f'admin:species_{obj.group.nature}portrait_add')?species={obj.id}&language=de"
                    links.append(f'<a href="{{}}" class="addlink">{lang}</a>')
                    urls.append(url_with_params)

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


#
# Flora
#
class FloraportraitForm(forms.ModelForm):
    class Meta:
        model = Floraportrait
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['species'].queryset = Species.objects.filter(group__nature='flora')


@admin.register(Floraportrait)
class FloraportraitAdmin(admin.ModelAdmin):
    form = FloraportraitForm
    list_display = ["species__speciesid", "species__group", "species__gername", "language"]
    search_fields = ('species__species_names__name',)
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published', 'language')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline
    ]
    ordering = ('species__gername',)


#
# Fauna
#
class FaunaportraitForm(forms.ModelForm):
    class Meta:
        model = Faunaportrait
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['species'].queryset = Species.objects.filter(group__nature='fauna')


@admin.register(Faunaportrait)
class FaunaportraitAdmin(admin.ModelAdmin):
    form = FaunaportraitForm
    list_display = ["species__speciesid", "species__group", "species__gername", "language"]
    search_fields = ('species__species_names__name', 'species__gername',)
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published', 'language')
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline
    ]
    ordering = ["species__gername"]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    radio_fields = {"nature": admin.VERTICAL}
    list_display = ['name', 'nature']
    list_filter = ['nature']


@admin.register(Avatar)
class AvatarAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['image_tag', 'image', 'image_owner']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image.url))


@admin.register(DescriptionImage)
class DescriptionImageAdmin(admin.ModelAdmin):
    pass
