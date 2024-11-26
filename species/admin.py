from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.html import format_html

from .models import Species, Group, Floraportrait, Faunaportrait, SpeciesName, Source, GoodToKnow, Avatar
from image_cropping import ImageCroppingMixin


class SpeciesNameInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        primary_counts = dict()
        lang_counts = dict()

        for form in self.forms:
            # Skip forms marked for deletion
            if form.cleaned_data.get('DELETE', False):
                continue

            language = form.cleaned_data.get('language')
            is_primary = form.cleaned_data.get('isPrimary')
            lang_counts[language] = lang_counts.get(language) or 0

            if is_primary:
                primary_counts[language] = (primary_counts.get(language) or 0) + 1

        sf_count = primary_counts.get('sf')
        if not sf_count or sf_count < 1:
            raise ValidationError("Es muss mind. einen primären wissenschaftlichen Namen geben")

        if any(value > 1 for value in primary_counts.values()):
            raise ValidationError("Es darf immer nur einen primären Namen pro Sprache geben")

        for lang in lang_counts.keys():
            count = primary_counts.get(lang)
            if not count or count < 1:
                raise ValidationError("Für jede vorhandene Sprache muss mind. ein primärer Name vergeben seien")


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1
    formset = SpeciesNameInlineFormSet


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline
    ]
    exclude = ["created_by"]
    readonly_fields = ["speciesid"]
    list_display = ["speciesid", 'get_primary_name', 'get_gername', 'group', 'group__nature']
    list_filter = ('group__nature', 'group')
    search_fields = ["species_names__name"]

    def get_primary_name(self, obj):
        primary_name = obj.species_names.filter(isPrimary=True, language="sf").first()
        return primary_name.name if primary_name else "N/A"

    get_primary_name.short_description = "Scientific name"

    def get_gername(self, obj):
        gername = obj.species_names.filter(isPrimary=True, language="de").first()
        return gername.name if gername else "N/A"

    get_gername.short_description = "German name"


#
# Portrait
#
class SourceInline(admin.TabularInline):
    model = Source
    extra = 0


class GoodToKnowInline(admin.TabularInline):
    model = GoodToKnow
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
    list_filter = ('published',)
    inlines = [
        SourceInline, GoodToKnowInline
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
    list_filter = ('published',)
    inlines = [
        SourceInline, GoodToKnowInline
    ]


admin.site.register(Group)


@admin.register(Avatar)
class AvatarAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['image_tag', 'image', 'image_owner']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image.url))
