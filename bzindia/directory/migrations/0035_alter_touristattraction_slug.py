# Generated by Django 5.1.4 on 2025-01-15 10:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0034_alter_touristattraction_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristattraction',
            name='slug',
            field=models.SlugField(default=uuid.UUID('7eb494c8-da26-4a43-a12e-26762881bda9')),
        ),
    ]
