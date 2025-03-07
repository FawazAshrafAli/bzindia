# Generated by Django 5.1.4 on 2025-02-03 09:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_alter_testimonial_image'),
        ('registration', '0004_alter_registrationdetail_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('slug', models.SlugField(blank=True, max_length=500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_faq_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationtype')),
            ],
            options={
                'db_table': 'registration_faqs',
                'ordering': ['-created'],
            },
        ),
    ]
