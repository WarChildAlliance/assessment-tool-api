# Generated by Django 3.2 on 2021-08-13 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('answers', '0004_auto_20210617_0913'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='duration',
        ),
        migrations.AddField(
            model_name='answer',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='start_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
