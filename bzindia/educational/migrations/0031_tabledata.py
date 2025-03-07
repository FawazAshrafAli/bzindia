# Generated by Django 5.1.4 on 2025-01-22 10:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0030_tableheading'),
    ]

    operations = [
        migrations.CreateModel(
            name='TableData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('table_heading', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.tableheading')),
            ],
            options={
                'db_table': 'table_datas',
                'ordering': ['created'],
            },
        ),
    ]
