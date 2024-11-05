from django.contrib import admin
from django import forms

from .models import Species, Group, Floraportrait, Faunaportrait, SpeciesName


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline,
    ]
    exclude = ["created_by"]
    readonly_fields = ["speciesid"]
    list_display = ["sciname", "name", "group", "group__nature"]
    list_filter = ('group__nature', 'group')
    search_fields = ["sciname", "name"]

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
    list_display = ('species',)
    search_fields = ('species__name',)
    list_filter = ('published',)


admin.site.register(Group)
