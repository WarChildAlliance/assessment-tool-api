# Generated by Django 4.0.5 on 2022-09-22 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0036_auto_20220922_1741'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionselect',
            name='multiple',
        ),
        migrations.RemoveField(
            model_name='draggableoption',
            name='area_option',
        ),
        migrations.RenameField(
            model_name='draggableoption',
            old_name='_area_option',
            new_name='area_option',
        ),
    ]
