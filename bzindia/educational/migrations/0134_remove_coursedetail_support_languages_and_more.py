# Generated by Django 5.1.4 on 2025-04-02 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0133_coursedetail_support_languages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursedetail',
            name='support_languages',
        ),
        migrations.AddField(
            model_name='coursedetail',
            name='hide_support_languages',
            field=models.BooleanField(default=False),
        ),
    ]
