from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.urls import reverse
from django.utils.html import format_html
from image_cropping import ImageCroppingMixin

from .models import Species, Group, Floraportrait, Faunaportrait, SpeciesName, Source, GoodToKnow, Avatar, \
    SimilarSpecies, AdditionalLink, UnambigousFeature, DescriptionImage


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline
    ]
    readonly_fields = ['speciesid']
    list_display = ['speciesid', 'gername', 'sciname', 'group', 'group__nature', 'portrait']
    list_filter = ('group__nature', 'group')
    search_fields = ["species_names__name"]
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

    def portrait(self, obj):
        if isinstance(obj.portrait, Floraportrait):
            app_label = obj.portrait._meta.app_label
            return reverse(f"admin:{app_label}_Floraportrait_change", args=[obj.portrait.pk])
        elif isinstance(obj.portrait, Faunaportrait):
            app_label = obj.portrait._meta.app_label
            return reverse(f"admin:{app_label}_Faunaportrait_change", args=[obj.portrait.pk])
        else:
            return "N/A"


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
        self.fields['species'].queryset = Species.objects.filter(group__nature='Flora')


@admin.register(Floraportrait)
class FloraportraitAdmin(admin.ModelAdmin):
    form = FloraportraitForm
    list_display = ["species__speciesid", "species__group"]
    search_fields = ('species__species_names__name',)
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published',)
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline
    ]


#
# Fauna
#
class FaunaportraitForm(forms.ModelForm):
    class Meta:
        model = Faunaportrait
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['species'].queryset = Species.objects.filter(group__nature='Fauna')


@admin.register(Faunaportrait)
class FaunaportraitAdmin(admin.ModelAdmin):
    form = FaunaportraitForm
    list_display = ["species__speciesid", "species__group"]
    search_fields = ('species__species_names__name',)
    search_help_text = 'Sucht über alle Artnamen'
    list_filter = ('published',)
    inlines = [
        UnambigousFeatureInline, SimilarSpeciesInline, GoodToKnowInline, AdditionalLinkInline, SourceInline
    ]


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
