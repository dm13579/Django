# Generated by Django 2.0.4 on 2018-10-29 05:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0013_creategedan'),
    ]

    operations = [
        migrations.RenameField(
            model_name='creategedan',
            old_name='column',
            new_name='gedanname',
        ),
    ]
