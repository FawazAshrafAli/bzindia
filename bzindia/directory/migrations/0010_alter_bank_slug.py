# Generated by Django 5.1.4 on 2024-12-05 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0009_alter_bank_swift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='slug',
            field=models.SlugField(blank=True, max_length=500, null=True),
        ),
    ]
