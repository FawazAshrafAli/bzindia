# Generated by Django 5.1.4 on 2025-03-27 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_rename_tag_metatag_alter_metatag_table'),
        ('educational', '0127_remove_multipage_meta_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='multipage',
            name='meta_tags',
            field=models.ManyToManyField(to='base.metatag'),
        ),
    ]
