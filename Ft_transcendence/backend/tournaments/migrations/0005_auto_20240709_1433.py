# Generated by Django 3.2.25 on 2024-07-09 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0004_tournament_force_end_tournament'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='blockchain_stored',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tournament',
            name='is_finished',
            field=models.BooleanField(default=False),
        ),
    ]
