# Generated by Django 3.2 on 2021-10-06 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0023_auto_20210928_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnumberline',
            name='tick_step',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='questionnumberline',
            name='step',
            field=models.IntegerField(default=1),
        ),
    ]
