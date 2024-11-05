from modeltranslation.translator import translator, TranslationOptions
from .models import Species

class SpeciesTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(Species, SpeciesTranslationOptions)
