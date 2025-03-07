# Generated by Django 5.1.4 on 2025-01-30 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0007_client'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='client',
            name='slug',
            field=models.SlugField(blank=True, max_length=500, null=True, unique=True),
        ),
    ]
