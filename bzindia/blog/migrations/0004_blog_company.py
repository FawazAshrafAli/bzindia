# Generated by Django 5.1.4 on 2025-02-13 14:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_blog_meta_description_blog_meta_tags_blog_summary'),
        ('company', '0016_multipage'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.company'),
        ),
    ]
