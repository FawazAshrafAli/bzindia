# Generated by Django 5.1.4 on 2025-02-04 11:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_alter_testimonial_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('slug', models.SlugField(blank=True, max_length=500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='multi_page_company', to='company.company')),
            ],
            options={
                'db_table': 'multipages',
                'ordering': ['created'],
            },
        ),
    ]
