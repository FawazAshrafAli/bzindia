# Generated by Django 5.1.4 on 2024-12-19 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0005_alter_company_favicon_alter_company_logo'),
        ('service', '0002_alter_category_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, max_length=500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.category')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_sub_category_company', to='company.company')),
            ],
            options={
                'db_table': 'service_sub_category',
                'ordering': ['name'],
            },
        ),
    ]
