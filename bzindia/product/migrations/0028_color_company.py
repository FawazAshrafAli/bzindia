# Generated by Django 5.1.2 on 2024-11-21 15:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0005_alter_company_favicon_alter_company_logo'),
        ('product', '0027_size_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='color',
            name='company',
            field=models.ForeignKey(default=16, on_delete=django.db.models.deletion.CASCADE, to='company.company'),
            preserve_default=False,
        ),
    ]