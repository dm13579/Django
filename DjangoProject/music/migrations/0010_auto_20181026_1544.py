# Generated by Django 2.0.4 on 2018-10-26 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0009_auto_20181026_1540'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commentsongsecond',
            old_name='hufupeople',
            new_name='huifupeople',
        ),
        migrations.AlterField(
            model_name='commentsongsecond',
            name='commentator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comtaor', to='music.Commentsong'),
        ),
    ]
