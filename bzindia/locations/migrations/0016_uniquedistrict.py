# Generated by Django 5.1.4 on 2025-01-14 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0015_uniquestate'),
    ]

    operations = [
        migrations.CreateModel(
            name='UniqueDistrict',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(blank=True, max_length=500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.state')),
            ],
            options={
                'db_table': 'unique_districts',
                'ordering': ['name'],
            },
        ),
    ]
