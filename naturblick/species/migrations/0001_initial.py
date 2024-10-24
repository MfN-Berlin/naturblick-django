# Generated by Django 5.1.2 on 2024-10-21 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('speciesid', models.CharField(max_length=255, unique=True)),
                ('sciname', models.CharField(max_length=255)),
                ('group', models.CharField(default='none', max_length=255)),
                ('gername', models.CharField(blank=True, max_length=255, null=True)),
                ('engname', models.CharField(blank=True, max_length=255, null=True)),
                ('easyname', models.CharField(blank=True, max_length=255, null=True)),
                ('gbifusagekey', models.IntegerField(blank=True, null=True)),
                ('accepted', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
