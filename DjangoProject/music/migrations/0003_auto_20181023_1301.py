# Generated by Django 2.0.4 on 2018-10-23 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_remove_playlist_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='music_albumimg',
            field=models.TextField(blank=True),
        ),
    ]