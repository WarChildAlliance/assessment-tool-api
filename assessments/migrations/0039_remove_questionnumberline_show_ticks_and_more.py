# Generated by Django 4.0.5 on 2022-09-21 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0038_auto_20220926_1210'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionnumberline',
            name='show_ticks',
        ),
        migrations.RemoveField(
            model_name='questionnumberline',
            name='show_value',
        ),
        migrations.RemoveField(
            model_name='questionnumberline',
            name='tick_step',
        ),
    ]