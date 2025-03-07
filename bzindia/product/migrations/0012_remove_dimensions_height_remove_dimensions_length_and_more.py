# Generated by Django 5.1.2 on 2024-11-11 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_alter_product_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dimensions',
            name='height',
        ),
        migrations.RemoveField(
            model_name='dimensions',
            name='length',
        ),
        migrations.RemoveField(
            model_name='dimensions',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='dimensions',
            name='width',
        ),
        migrations.RemoveField(
            model_name='product',
            name='dimensions',
        ),
        migrations.AddField(
            model_name='product',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
