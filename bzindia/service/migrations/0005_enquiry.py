# Generated by Django 5.1.4 on 2025-01-18 10:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0006_company_description'),
        ('locations', '0018_uniqueplace'),
        ('service', '0004_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('slug', models.SlugField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_enquiry_company', to='company.company')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.service')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.uniquestate')),
            ],
            options={
                'db_table': 'service_enquiries',
                'ordering': ['-created'],
            },
        ),
    ]
