# Generated by Django 5.1.4 on 2024-12-31 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0007_alter_program_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='specialization',
        ),
    ]
