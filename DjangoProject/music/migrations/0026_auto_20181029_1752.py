# Generated by Django 2.0.4 on 2018-10-29 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0025_auto_20181029_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='gedansong',
            name='music_album',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='gedansong',
            name='music_album_id',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='gedansong',
            name='music_artist',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='gedansong',
            name='music_artist_id',
            field=models.TextField(blank=True),
        ),
    ]
