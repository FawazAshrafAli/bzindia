# Generated by Django 5.1.2 on 2024-11-13 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0009_alter_district_slug_alter_place_slug_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetestedCoordinates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
    ]
