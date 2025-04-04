# Generated by Django 5.1.4 on 2025-03-07 10:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0018_metatag'),
        ('service', '0014_verticaltab'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorizontalBullet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('bullet', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_horizontal_bullet_company', to='company.company')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.service')),
            ],
            options={
                'db_table': 'service_horizontal_bullets',
                'ordering': ['created'],
            },
        ),
    ]
