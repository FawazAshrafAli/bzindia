# Generated by Django 5.1.4 on 2024-12-07 17:42

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0016_remove_touristattraction_name_english_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristattraction',
            name='slug',
            field=models.SlugField(default=uuid.UUID('f59ec81f-4438-4a02-aab3-8547d0665741')),
        ),
    ]