# Generated by Django 5.1.4 on 2025-03-27 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_rename_tag_metatag_alter_metatag_table'),
        ('product', '0044_remove_multipage_meta_tags_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='multipage',
            name='meta_tags',
            field=models.ManyToManyField(related_name='meta_tag_of_multipage', to='base.metatag'),
        ),
    ]
