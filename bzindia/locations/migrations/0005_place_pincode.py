# Generated by Django 5.1.2 on 2024-11-07 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_place_latitude_place_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='pincode',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]