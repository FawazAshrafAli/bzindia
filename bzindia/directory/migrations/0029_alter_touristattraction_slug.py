# Generated by Django 5.1.4 on 2025-01-14 15:25

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0028_alter_touristattraction_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristattraction',
            name='slug',
            field=models.SlugField(default=uuid.UUID('4c940a7e-c554-4981-bd87-c39ffab74e61')),
        ),
    ]
