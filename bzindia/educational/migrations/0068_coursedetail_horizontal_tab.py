# Generated by Django 5.1.4 on 2025-01-22 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0067_coursedetail_horizontal_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursedetail',
            name='horizontal_tab',
            field=models.ManyToManyField(to='educational.horizontaltab'),
        ),
    ]
