# Generated by Django 5.1.5 on 2025-02-04 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mypp', '0002_place_tips'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='events',
            field=models.JSONField(default=list),
        ),
    ]
