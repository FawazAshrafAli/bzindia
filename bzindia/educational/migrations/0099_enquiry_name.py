# Generated by Django 5.1.4 on 2025-02-04 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational', '0098_testimonial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enquiry',
            name='name',
            field=models.CharField(default='Satheesh Kumar', max_length=250),
            preserve_default=False,
        ),
    ]
