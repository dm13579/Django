# Generated by Django 2.0.4 on 2018-10-22 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='user',
        ),
    ]