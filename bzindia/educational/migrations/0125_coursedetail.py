# Generated by Django 5.1.4 on 2025-03-26 17:00

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0020_delete_metatag'),
        ('educational', '0124_delete_coursedetail'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField()),
                ('description', ckeditor.fields.RichTextField()),
                ('meta_title', models.CharField(max_length=100)),
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
                ('bullet_points', models.ManyToManyField(to='educational.bulletpoints')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
                ('features', models.ManyToManyField(to='educational.feature')),
                ('horizontal_tabs', models.ManyToManyField(to='educational.horizontaltab')),
                ('tables', models.ManyToManyField(to='educational.table')),
                ('tags', models.ManyToManyField(to='educational.tag')),
                ('timelines', models.ManyToManyField(to='educational.timeline')),
                ('vertical_tabs', models.ManyToManyField(to='educational.verticaltab')),
            ],
            options={
                'db_table': 'course_details',
                'ordering': ['created'],
            },
        ),
    ]
