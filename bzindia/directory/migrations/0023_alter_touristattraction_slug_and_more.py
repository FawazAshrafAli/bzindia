# Generated by Django 5.1.4 on 2024-12-10 17:23

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0022_policestation_name_assamese_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristattraction',
            name='slug',
            field=models.SlugField(default=uuid.UUID('7b259db4-0f57-4bec-a965-89011fb44799')),
        ),
        migrations.AlterModelTable(
            name='policestation',
            table='police_stations',
        ),
    ]