# Generated by Django 5.1.2 on 2024-11-11 11:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='dimensions',
            name='product_obj',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='product_dimension', to='product.product'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dimensions',
            name='unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]