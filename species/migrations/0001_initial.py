# Generated by Django 5.1.2 on 2025-04-09 13:40

import django.core.validators
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware
import image_cropping.fields
import species.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=255, upload_to='avatar_images')),
                ('owner', models.CharField(max_length=255)),
                ('owner_link', models.URLField(blank=True, max_length=255, null=True)),
                ('source', models.URLField(max_length=1024)),
                ('license', models.CharField(max_length=64)),
                ('cropping', image_cropping.fields.ImageRatioField('image', '400x400', adapt_rotation=False, allow_fullsize=False, free_crop=False, help_text=None, hide_image_field=False, size_warning=True, verbose_name='cropping')),
            ],
            options={
                'db_table': 'avatar',
            },
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('gername', models.CharField(max_length=255, verbose_name='German name')),
                ('engname', models.CharField(max_length=255, verbose_name='English name')),
                ('display_name', models.CharField(blank=True, max_length=255, null=True)),
                ('weight', models.IntegerField()),
                ('single_choice', models.BooleanField(blank=True, null=True)),
                ('gerdescription', models.TextField(blank=True, null=True, verbose_name='German description')),
                ('engdescription', models.TextField(blank=True, null=True, verbose_name='English description')),
            ],
            options={
                'db_table': 'character',
            },
        ),
        migrations.CreateModel(
            name='Portrait',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('en', 'English'), ('de', 'German'), ('dels', 'German Easy Read')], max_length=4)),
                ('short_description', models.TextField(help_text='Kurze Beschreibung für den schnellen Überblick draußen.')),
                ('city_habitat', models.TextField(help_text='Beschreibung Lebensraum in der Stadt, besondere Anpassungen an die Stadt.')),
                ('human_interaction', models.TextField(blank=True, help_text='Typische Interaktion mit dem Menschen, z.B. gestalterische Nutzung, Gefährdung durch menschliche Aktivität, Verbreitung.', null=True)),
                ('published', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'portrait',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('nature', models.CharField(choices=[('fauna', 'Fauna'), ('flora', 'Flora')], max_length=5, null=True)),
            ],
            options={
                'db_table': 'group',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PortraitImageFile',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('owner', models.CharField(max_length=255)),
                ('owner_link', models.URLField(blank=True, max_length=255, null=True)),
                ('source', models.URLField(max_length=1024)),
                ('license', models.CharField(max_length=64)),
                ('image', models.ImageField(height_field='height', max_length=255, upload_to='portrait_images', width_field='width')),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'portrait_image_file',
            },
        ),
        migrations.CreateModel(
            name='SourcesImprint',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('sound_recogniotion_images', 'Lauterkennung Bilder'), ('sound_recogniotion_sounds', 'Lauterkennung Tonaufnahmen'), ('ident_keys', 'Bestimmungsschlüssel')], max_length=32, verbose_name='Group')),
                ('scie_name', models.CharField(max_length=255, verbose_name='German description')),
                ('scie_name_eng', models.CharField(blank=True, max_length=255, null=True, verbose_name='English description')),
                ('image_source', models.CharField(blank=True, max_length=255, null=True)),
                ('image_link', models.CharField(blank=True, max_length=255, null=True)),
                ('licence', models.CharField(blank=True, max_length=255, null=True)),
                ('author', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'sources_imprint',
            },
        ),
        migrations.CreateModel(
            name='SourcesTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('en', 'English'), ('de', 'German'), ('dels', 'German Easy Read'), ('sf', 'Scientific')], max_length=4)),
                ('key', models.CharField(choices=[('page', 'Page'), ('wiki', 'Wiki'), ('revision', 'Revision'), ('accessed', 'Accessed'), ('version', 'Version'), ('volume', 'Volume'), ('editors', 'Editors'), ('nodate', 'Nodate'), ('in', 'In'), ('published', 'Published'), ('edition', 'Edition'), ('part', 'Part'), ('changedby', 'Changed by')], max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'sources_translation',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='German name')),
                ('english_name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'tag',
            },
        ),
        migrations.CreateModel(
            name='CharacterValue',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('gername', models.CharField(max_length=255, verbose_name='German name')),
                ('engname', models.CharField(max_length=255, verbose_name='English name')),
                ('colors', models.CharField(blank=True, max_length=255, null=True)),
                ('dots', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(max_length=255, null=True, upload_to='character_images')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.character')),
            ],
            options={
                'db_table': 'character_value',
            },
        ),
        migrations.CreateModel(
            name='Floraportrait',
            fields=[
                ('portrait_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='species.portrait')),
                ('leaf_description', models.TextField(help_text='Beschreibung Laubblatt: z.B. Form, Farbe, Blattstellung, besondere Merkmale.')),
                ('stem_axis_description', models.TextField(help_text='Beschreibung Stängel/Stamm: z.B. Wuchsrichtung, Verzweigung, Farbe, besondere Merkmale.')),
                ('flower_description', models.TextField(help_text='Beschreibung Blüte/Blütenstand: z.B. Farbe, Blütenstandsform, besondere Merkmale.')),
                ('fruit_description', models.TextField(help_text='Bechreibung Frucht/Fruchstand: z.B. Form, Farbe, Oberfläche, besondere Merkmale.')),
            ],
            options={
                'db_table': 'floraportrait',
            },
            bases=('species.portrait',),
        ),
        migrations.CreateModel(
            name='AdditionalLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('url', models.URLField(max_length=255)),
                ('order', models.IntegerField()),
                ('portrait', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
            ],
            options={
                'db_table': 'additional_link',
            },
        ),
        migrations.CreateModel(
            name='GoodToKnow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fact', models.TextField()),
                ('type', models.CharField(choices=[('usage', 'Usage'), ('mnemonic', 'Mnemonic'), ('culturalhistory', 'Culturalhistory'), ('art', 'Art'), ('music', 'Music'), ('literature', 'Literature'), ('originofname', 'Origin of name'), ('origin', 'Origin'), ('toxicityorusage', 'Toxicity or usage'), ('other', 'Other')], max_length=15)),
                ('order', models.IntegerField()),
                ('portrait', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
            ],
            options={
                'db_table': 'good_to_know',
            },
        ),
        migrations.AddField(
            model_name='character',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='species.group'),
        ),
        migrations.CreateModel(
            name='InTheCityMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_orientation', models.CharField(choices=[('horizontal', 'horizontal'), ('vertical', 'vertical')], max_length=10, null=True)),
                ('display_ratio', models.CharField(choices=[('4-3', '4-3'), ('3-4', '3-4')], max_length=3)),
                ('grid_ratio', models.CharField(choices=[('1-2', '1-2'), ('5-7', '5-7'), ('1-1', '1-1'), ('7-5', '7-5'), ('2-1', '2-1')], max_length=3)),
                ('focus_point_vertical', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('focus_point_horizontal', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('text', models.CharField(max_length=255)),
                ('portrait', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
                ('portrait_image_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portraitimagefile')),
            ],
            options={
                'db_table': 'inthecity_meta',
            },
        ),
        migrations.CreateModel(
            name='FunFactMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_orientation', models.CharField(choices=[('horizontal', 'horizontal'), ('vertical', 'vertical')], max_length=10, null=True)),
                ('display_ratio', models.CharField(choices=[('4-3', '4-3'), ('3-4', '3-4')], max_length=3)),
                ('grid_ratio', models.CharField(choices=[('1-2', '1-2'), ('5-7', '5-7'), ('1-1', '1-1'), ('7-5', '7-5'), ('2-1', '2-1')], max_length=3)),
                ('focus_point_vertical', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('focus_point_horizontal', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('text', models.CharField(max_length=255)),
                ('portrait', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
                ('portrait_image_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portraitimagefile')),
            ],
            options={
                'db_table': 'funfact_meta',
            },
        ),
        migrations.CreateModel(
            name='DescMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_orientation', models.CharField(choices=[('horizontal', 'horizontal'), ('vertical', 'vertical')], max_length=10, null=True)),
                ('display_ratio', models.CharField(choices=[('4-3', '4-3'), ('3-4', '3-4')], max_length=3)),
                ('grid_ratio', models.CharField(choices=[('1-2', '1-2'), ('5-7', '5-7'), ('1-1', '1-1'), ('7-5', '7-5'), ('2-1', '2-1')], max_length=3)),
                ('focus_point_vertical', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('focus_point_horizontal', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('text', models.CharField(max_length=255)),
                ('portrait', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
                ('portrait_image_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portraitimagefile')),
            ],
            options={
                'db_table': 'desc_meta',
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('order', models.IntegerField()),
                ('portrait', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
            ],
            options={
                'db_table': 'source',
            },
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('speciesid', models.CharField(max_length=255, unique=True)),
                ('gername', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='German name')),
                ('sciname', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Scientific name')),
                ('engname', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='English name')),
                ('nbclassid', models.CharField(blank=True, max_length=255, null=True)),
                ('wikipedia', models.URLField(blank=True, max_length=255, null=True, verbose_name='Wikipedia link')),
                ('autoid', models.BooleanField(default=False)),
                ('red_list_germany', models.CharField(blank=True, choices=[('gefahrdet', 'gefährdet'), ('Vorwarnliste', 'Vorwarnliste'), ('ausgestorben oder verschollen', 'ausgestorben oder verschollen'), ('vomAussterbenBedroht', 'vom Aussterben bedroht'), ('starkGefahrdet', 'stark gefährdet'), ('GefahrdungUnbekanntenAusmasses', 'Gefährdung unbekannten Ausmasses'), ('extremSelten', 'extrem selten'), ('DatenUnzureichend', 'Daten unzureichend'), ('ungefahrdet', 'ungefährdet'), ('nichtBewertet', 'nicht bewertet'), ('keinNachweis', 'kein Nachweis')], max_length=255, null=True)),
                ('iucncategory', models.CharField(blank=True, choices=[('NE', 'NE'), ('DD', 'DD'), ('LC', 'LC'), ('NT', 'NT'), ('VU', 'VU'), ('EN', 'EN'), ('CR', 'CR'), ('EW', 'EW'), ('EX', 'EX')], max_length=2, null=True)),
                ('activity_start_month', models.CharField(blank=True, choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], max_length=9, null=True)),
                ('activity_end_month', models.CharField(blank=True, choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], max_length=9, null=True)),
                ('activity_start_hour', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(23)])),
                ('activity_end_hour', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(23)])),
                ('gbifusagekey', models.IntegerField(blank=True, null=True, unique=True, verbose_name='GBIF usagekey')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('plantnetpowoid', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('accepted_species', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='species.species')),
                ('avatar', models.ForeignKey(blank='True', null='True', on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='species.avatar')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='species_created_by_set', to=settings.AUTH_USER_MODEL)),
                ('female_avatar', models.ForeignKey(blank='True', null='True', on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='species.avatar')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='species.group')),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='species_updated_by_set', to=settings.AUTH_USER_MODEL)),
                ('tag', models.ManyToManyField(blank=True, to='species.tag')),
            ],
            options={
                'verbose_name_plural': 'species',
                'db_table': 'species',
            },
        ),
        migrations.CreateModel(
            name='SimilarSpecies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('differences', models.TextField()),
                ('order', models.IntegerField()),
                ('portrait', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.species')),
            ],
            options={
                'db_table': 'similar_species',
            },
        ),
        migrations.AddField(
            model_name='portraitimagefile',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.species'),
        ),
        migrations.AddField(
            model_name='portrait',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='species.species'),
        ),
        migrations.CreateModel(
            name='FaunaportraitAudioFile',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('owner', models.CharField(max_length=255)),
                ('owner_link', models.URLField(blank=True, max_length=255, null=True)),
                ('source', models.URLField(max_length=1024)),
                ('license', models.CharField(max_length=64)),
                ('audio_file', models.FileField(blank=True, null=True, upload_to='audio_files', validators=[species.validators.validate_mp3])),
                ('audio_spectrogram', models.ImageField(blank=True, null=True, upload_to='spectrogram_images', validators=[species.validators.validate_png])),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.species')),
            ],
            options={
                'db_table': 'faunaportrait_audio_file',
            },
        ),
        migrations.CreateModel(
            name='SpeciesName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('language', models.CharField(choices=[('en', 'English'), ('de', 'German'), ('dels', 'German Easy Read'), ('sf', 'Scientific')], max_length=4)),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.species')),
            ],
            options={
                'db_table': 'species_name',
            },
        ),
        migrations.CreateModel(
            name='UnambigousFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('order', models.IntegerField()),
                ('portrait', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.portrait')),
            ],
            options={
                'db_table': 'unambigous_feature',
            },
        ),
        migrations.CreateModel(
            name='Faunaportrait',
            fields=[
                ('portrait_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='species.portrait')),
                ('male_description', models.TextField(blank=True, help_text='Kurze Ergänzungen zu abweichenden Merkmalen der Männchen.', null=True)),
                ('female_description', models.TextField(blank=True, help_text='Kurze Ergänzungen zu abweichenden Merkmalen der Weibchen.', null=True)),
                ('juvenile_description', models.TextField(blank=True, help_text='Kurze Ergänzungen zu abweichenden Merkmalen der Jugendstadien.', null=True)),
                ('tracks', models.TextField(blank=True, help_text='Kurze Beschreibung zur Bestimmung anhand der Trittsiegel.', null=True)),
                ('audio_title', models.CharField(blank=True, max_length=255, null=True)),
                ('faunaportrait_audio_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='species.faunaportraitaudiofile')),
            ],
            options={
                'db_table': 'faunaportrait',
            },
            bases=('species.portrait',),
        ),
        migrations.AddConstraint(
            model_name='portrait',
            constraint=models.UniqueConstraint(fields=('species', 'language'), name='unique_species_language'),
        ),
        migrations.AddConstraint(
            model_name='speciesname',
            constraint=models.UniqueConstraint(fields=('species', 'name', 'language'), name='unique_species_name'),
        ),
    ]
