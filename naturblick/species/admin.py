from django.contrib import admin

from .models import Species, Group, Floraportrait, Faunaportrait, SpeciesName


class SpeciesNameInline(admin.TabularInline):
    model = SpeciesName
    extra = 1

class SpeciesAdmin(admin.ModelAdmin):
    inlines = [
        SpeciesNameInline,
    ]
    exclude = ["created_by"]
    readonly_fields = ["speciesid"]



admin.site.register(Group)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(Floraportrait)
admin.site.register(Faunaportrait)