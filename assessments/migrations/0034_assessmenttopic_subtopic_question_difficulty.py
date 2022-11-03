# Generated by Django 4.0.5 on 2022-09-16 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0033_merge_20220811_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmenttopic',
            name='subtopic',
            field=models.CharField(choices=[('Subtopic 1', 'Subtopic 1'), ('Subtopic 2', 'Subtopic 2'), ('Subtopic 3', 'Subtopic 3')], max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='difficulty',
            field=models.IntegerField(choices=[(1, 'Difficulty 1'), (2, 'Difficulty 2'), (3, 'Difficulty 3')], null=True),
        ),
    ]
