# Generated by Django 2.0.4 on 2018-10-29 06:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0019_remove_gedansong_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gedansong',
            name='gedan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gedansong', to='music.Creategedan'),
        ),
    ]