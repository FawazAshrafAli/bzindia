# Generated by Django 5.1.4 on 2024-12-05 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0007_bank'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='bank',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
    ]