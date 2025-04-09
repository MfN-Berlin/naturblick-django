MONTH_CHOICES = [
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]

IUCN_CHOICES = [
    ('NE', 'NE'),
    ('DD', 'DD'),
    ('LC', 'LC'),
    ('NT', 'NT'),
    ('VU', 'VU'),
    ('EN', 'EN'),
    ('CR', 'CR'),
    ('EW', 'EW'),
    ('EX', 'EX'),
]

REDLIST_CHOICES = [
    ('gefahrdet', 'gefährdet'),
    ('Vorwarnliste', 'Vorwarnliste'),
    ('ausgestorben oder verschollen', 'ausgestorben oder verschollen'),
    ('vomAussterbenBedroht', 'vom Aussterben bedroht'),
    ('starkGefahrdet', 'stark gefährdet'),
    ('GefahrdungUnbekanntenAusmasses', 'Gefährdung unbekannten Ausmasses'),
    ('extremSelten', 'extrem selten'),
    ('DatenUnzureichend', 'Daten unzureichend'),
    ('ungefahrdet', 'ungefährdet'),
    ('nichtBewertet', 'nicht bewertet'),
    ('keinNachweis', 'kein Nachweis'),
]

NATURE_CHOICES = [
    ('fauna', 'Fauna'),
    ('flora', 'Flora'),
]

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('de', 'German'),
    ('dels', 'German Easy Read'),
]

NAME_LANGUAGE_CHOICES = LANGUAGE_CHOICES + [('sf', 'Scientific')]

GOOD_TO_KNOW_CHOICES = [
    ('usage', 'Usage'),
    ('mnemonic', 'Mnemonic'),
    ('culturalhistory', 'Culturalhistory'),
    ('art', 'Art'),
    ('music', 'Music'),
    ('literature', 'Literature'),
    ('originofname', 'Origin of name'),
    ('origin', 'Origin'),
    ('toxicityorusage', 'Toxicity or usage'),
    ('other', 'Other'),
]

IMAGE_ORIENTATION_CHOICES = [
    ('horizontal', 'horizontal'),
    ('vertical', 'vertical'),
]

DISPLAY_RATIO_CHOICES = [
    ('4-3', '4-3'),
    ('3-4', '3-4'),
]

GRID_RATIO_CHOICES = [
    ('1-2', '1-2'),
    ('5-7', '5-7'),
    ('1-1', '1-1'),
    ('7-5', '7-5'),
    ('2-1', '2-1'),
]

PORTRAIT_IMAGE_TYPE_CHOICES = [
    ('description', 'Description'),
    ('in_the_city', 'In the city'),
    ('fun_fact', 'Fun fact'),
]

SOURCES_IMPRINT_CHOICES = [
    ('sound_recogniotion_images', 'Lauterkennung Bilder'),
    ('sound_recogniotion_sounds', 'Lauterkennung Tonaufnahmen'),
    ('ident_keys', 'Bestimmungsschlüssel'),
]

SOURCES_TRANSLATION_CHOICES= [
    ('page', 'Page'),
    ('wiki', 'Wiki'),
    ('revision', 'Revision'),
    ('accessed', 'Accessed'),
    ('version', 'Version'),
    ('volume', 'Volume'),
    ('editors', 'Editors'),
    ('nodate', 'Nodate'),
    ('in', 'In'),
    ('published', 'Published'),
    ('edition', 'Edition'),
    ('part', 'Part'),
    ('changedby', 'Changed by'),
]



