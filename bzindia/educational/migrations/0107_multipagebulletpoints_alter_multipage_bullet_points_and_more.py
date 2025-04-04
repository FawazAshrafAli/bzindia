# Generated by Django 5.1.4 on 2025-03-20 16:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0019_delete_multipage'),
        ('educational', '0106_multipage'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiPageBulletPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bullet_point', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_bullet_points',
                'ordering': ['created'],
            },
        ),
        migrations.AlterField(
            model_name='multipage',
            name='bullet_points',
            field=models.ManyToManyField(to='educational.multipagebulletpoints'),
        ),
        migrations.CreateModel(
            name='MultiPageFaq',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qusetion', models.CharField(max_length=250)),
                ('answer', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_faqs',
                'ordering': ['created'],
            },
        ),
        migrations.AddField(
            model_name='multipage',
            name='faqs',
            field=models.ManyToManyField(to='educational.multipagefaq'),
        ),
        migrations.CreateModel(
            name='MultiPageFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_features',
                'ordering': ['created'],
            },
        ),
        migrations.AlterField(
            model_name='multipage',
            name='features',
            field=models.ManyToManyField(to='educational.multipagefeature'),
        ),
        migrations.CreateModel(
            name='MultiPageHorizontalBullet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('bullet', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_horizontal_bullets',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='MultiPageHorizontalTab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('bullets', models.ManyToManyField(to='educational.horizontalbullet')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_horizontal_tabs',
                'ordering': ['created'],
            },
        ),
        migrations.AlterField(
            model_name='multipage',
            name='horizontal_tabs',
            field=models.ManyToManyField(to='educational.multipagehorizontaltab'),
        ),
        migrations.CreateModel(
            name='MultiPageTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
                ('datas', models.ManyToManyField(to='educational.tabledata')),
            ],
            options={
                'db_table': 'course_multipage_table',
                'ordering': ['created'],
            },
        ),
        migrations.AlterField(
            model_name='multipage',
            name='tables',
            field=models.ManyToManyField(to='educational.multipagetable'),
        ),
        migrations.CreateModel(
            name='MultiPageTableData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=250)),
                ('data', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_table_data',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='MultiPageTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=250)),
                ('link', models.URLField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_tags',
                'ordering': ['created'],
            },
        ),
        migrations.AlterField(
            model_name='multipage',
            name='tags',
            field=models.ManyToManyField(to='educational.multipagetag'),
        ),
        migrations.CreateModel(
            name='MultiPageTimeline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=250)),
                ('summary', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_timelines',
                'ordering': ['created'],
            },
        ),
        migrations.AlterField(
            model_name='multipage',
            name='timelines',
            field=models.ManyToManyField(to='educational.multipagetimeline'),
        ),
        migrations.CreateModel(
            name='MultiPageVerticalBullet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('sub_heading', models.CharField(blank=True, max_length=250, null=True)),
                ('bullet', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_vertical_bullets',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='MultiPageVerticalTab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(blank=True, max_length=250, null=True)),
                ('sub_heading', models.CharField(blank=True, max_length=250, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('bullets', models.ManyToManyField(to='educational.verticalbullet')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='educational.course')),
            ],
            options={
                'db_table': 'course_multipage_vertical_tabs',
                'ordering': ['created'],
            },
        ),
        migrations.AlterField(
            model_name='multipage',
            name='vertical_tabs',
            field=models.ManyToManyField(to='educational.multipageverticaltab'),
        ),
    ]
