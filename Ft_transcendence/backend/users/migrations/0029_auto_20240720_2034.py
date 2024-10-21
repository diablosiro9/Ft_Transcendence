# Generated by Django 3.2.25 on 2024-07-20 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_auto_20240720_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='twofactor_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
