# Generated by Django 5.1.4 on 2024-12-10 17:27

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0024_remove_policestation_osm_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policestation',
            name='opening_hours',
        ),
        migrations.AlterField(
            model_name='touristattraction',
            name='slug',
            field=models.SlugField(default=uuid.UUID('2d3cb649-43fb-48c5-bb47-25a68d91f500')),
        ),
    ]
