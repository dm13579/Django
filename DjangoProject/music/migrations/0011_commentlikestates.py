# Generated by Django 2.0.4 on 2018-10-27 04:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0010_auto_20181026_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commentlikestates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('states', models.TextField(max_length=2)),
                ('commentator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Commentlike', to='music.Commentsong')),
            ],
        ),
    ]
