# Generated by Django 5.1.4 on 2025-03-22 10:18

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0114_multipage_hide_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multipage',
            name='description',
            field=ckeditor.fields.RichTextField(default=None),
            preserve_default=False,
        ),
    ]
