# Generated by Django 5.1.2 on 2024-11-08 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0007_alter_testedcoordinates_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]