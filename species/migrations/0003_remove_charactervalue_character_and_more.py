# Generated by Django 5.1.2 on 2025-04-17 07:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('species', '0002_plantnetpowoidmapping'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charactervalue',
            name='character',
        ),
        migrations.AlterField(
            model_name='plantnetpowoidmapping',
            name='species_plantnetpowoid',
            field=models.ForeignKey(limit_choices_to={'plantnetpowoid__isnull': False}, on_delete=django.db.models.deletion.CASCADE, to='species.species', to_field='plantnetpowoid'),
        ),
        migrations.DeleteModel(
            name='Character',
        ),
        migrations.DeleteModel(
            name='CharacterValue',
        ),
    ]
