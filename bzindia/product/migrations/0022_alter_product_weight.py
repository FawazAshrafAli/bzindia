# Generated by Django 5.1.2 on 2024-11-18 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0021_product_sub_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]