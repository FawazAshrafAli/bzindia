# Generated by Django 5.1.2 on 2024-11-07 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_place_pincode'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestedCoordinates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.CharField(max_length=50)),
                ('longitude', models.CharField(max_length=50)),
            ],
        ),
    ]
