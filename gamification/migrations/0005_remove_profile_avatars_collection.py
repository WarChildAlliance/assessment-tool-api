# Generated by Django 3.2 on 2021-06-28 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0004_avatar_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='avatars_collection',
        ),
    ]