# Generated by Django 5.1.4 on 2025-03-27 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_rename_tag_metatag_alter_metatag_table'),
        ('product', '0043_remove_productdetailpage_meta_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multipage',
            name='meta_tags',
        ),
        migrations.AddField(
            model_name='productdetailpage',
            name='meta_tags',
            field=models.ManyToManyField(to='base.metatag'),
        ),
    ]
