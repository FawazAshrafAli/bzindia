# Generated by Django 5.1.4 on 2024-12-10 17:25

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0023_alter_touristattraction_slug_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policestation',
            name='osm_id',
        ),
        migrations.AlterField(
            model_name='touristattraction',
            name='slug',
            field=models.SlugField(default=uuid.UUID('decf14f9-1a50-4b62-89c3-31a97e1302b5')),
        ),
    ]
