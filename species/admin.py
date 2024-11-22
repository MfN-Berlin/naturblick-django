from django.contrib import admin
from django import forms
from django.utils.html import format_html

from .models import Species, Group, Floraportrait, Faunaportrait, SpeciesName, Source, GoodToKnow, Avatar
from image_cropping import ImageCroppingMixin

class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline
    ]
    exclude = ["created_by"]
    readonly_fields = ["speciesid"]
    list_display = ["sciname", "name", "group", "group__nature"]
    list_filter = ('group__nature', 'group')
    search_fields = ["sciname", "name"]


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
    list_display = ('species',)
    search_fields = ('species__name',)
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
    list_display = ["species__sciname", "species__group"]
    search_fields = ('species__sciname',)
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