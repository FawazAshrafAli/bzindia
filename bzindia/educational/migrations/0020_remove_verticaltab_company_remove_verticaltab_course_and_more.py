# Generated by Django 5.1.4 on 2025-01-21 17:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0019_coursedetail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verticaltab',
            name='company',
        ),
        migrations.RemoveField(
            model_name='verticaltab',
            name='course',
        ),
        migrations.AddField(
            model_name='verticaltab',
            name='course_detail',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='educational.coursedetail'),
            preserve_default=False,
        ),
    ]
