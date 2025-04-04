# Generated by Django 5.1.4 on 2025-03-24 14:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0019_delete_multipage'),
        ('registration', '0010_remove_multipage_registration_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulletPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bullet_point', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_bullet_points_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_bullet_points',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_feature_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_features',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='HorizontalBullet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('bullet', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_horizontal_bullet_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_horizontal_bullets',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='HorizontalTab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('bullets', models.ManyToManyField(to='registration.horizontalbullet')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_horizontal_tab_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_horizontal_tabs',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='TableData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=250)),
                ('data', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_table_data_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_table_data',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_table_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
                ('datas', models.ManyToManyField(to='registration.tabledata')),
            ],
            options={
                'db_table': 'registration_table',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=250)),
                ('link', models.URLField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_tag_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_tags',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=250)),
                ('summary', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_timeline_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_timelines',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='VerticalBullet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('sub_heading', models.CharField(blank=True, max_length=250, null=True)),
                ('bullet', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_vertical_bullet_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_vertical_bullets',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='VerticalTab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('sub_heading', models.CharField(blank=True, max_length=250, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('bullets', models.ManyToManyField(to='registration.verticalbullet')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_vertical_tab_company', to='company.company')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
            ],
            options={
                'db_table': 'registration_vertical_tabs',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='RegistrationDetailPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('meta_tags', models.CharField(max_length=250)),
                ('meta_description', models.TextField()),
                ('vertical_title', models.CharField(blank=True, max_length=250, null=True)),
                ('horizontal_title', models.CharField(blank=True, max_length=250, null=True)),
                ('table_title', models.CharField(blank=True, max_length=250, null=True)),
                ('bullet_title', models.CharField(blank=True, max_length=250, null=True)),
                ('tag_title', models.CharField(blank=True, max_length=250, null=True)),
                ('timeline_title', models.CharField(blank=True, max_length=250, null=True)),
                ('hide_features', models.BooleanField(default=False)),
                ('hide_vertical_tab', models.BooleanField(default=False)),
                ('hide_horizontal_tab', models.BooleanField(default=False)),
                ('hide_table', models.BooleanField(default=False)),
                ('hide_bullets', models.BooleanField(default=False)),
                ('hide_tags', models.BooleanField(default=False)),
                ('hide_timeline', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('bullet_points', models.ManyToManyField(to='registration.bulletpoint')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('features', models.ManyToManyField(to='registration.feature')),
                ('horizontal_tabs', models.ManyToManyField(to='registration.horizontaltab')),
                ('registration_sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationsubtype')),
                ('tables', models.ManyToManyField(to='registration.table')),
                ('tags', models.ManyToManyField(to='registration.tag')),
                ('timelines', models.ManyToManyField(to='registration.timeline')),
                ('vertical_tabs', models.ManyToManyField(to='registration.verticaltab')),
            ],
            options={
                'db_table': 'registration_detail_pages',
                'ordering': ['created'],
            },
        ),
    ]
