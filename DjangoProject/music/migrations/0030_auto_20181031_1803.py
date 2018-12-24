# Generated by Django 2.0.4 on 2018-10-31 10:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('music', '0029_guanzhu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guanzhu',
            name='guangzhu',
        ),
        migrations.AddField(
            model_name='guanzhu',
            name='guangzhufor',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='guanzhufor', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='guanzhu',
            name='guangzhuto',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.CASCADE, related_name='guanzhuto', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
