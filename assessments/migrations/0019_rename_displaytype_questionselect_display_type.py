# Generated by Django 3.2 on 2021-07-27 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0018_merge_20210726_0704'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionselect',
            old_name='displayType',
            new_name='display_type',
        ),
    ]
