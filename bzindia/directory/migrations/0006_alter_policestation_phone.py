# Generated by Django 5.1.4 on 2024-12-05 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0005_remove_policestation_tags_policestation_address_city_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policestation',
            name='phone',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
