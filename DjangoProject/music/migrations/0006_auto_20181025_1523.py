# Generated by Django 2.0.4 on 2018-10-25 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_comment'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Comment',
            new_name='Commentsong',
        ),
    ]