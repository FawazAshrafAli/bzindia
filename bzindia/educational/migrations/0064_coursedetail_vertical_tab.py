# Generated by Django 5.1.4 on 2025-01-22 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0063_coursedetail_vertical_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursedetail',
            name='vertical_tab',
            field=models.ManyToManyField(to='educational.verticaltab'),
        ),
    ]
