# Generated by Django 4.0.5 on 2022-11-28 17:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0011_alter_avatar_options'),
        ('assessments', '0049_merge_20221202_1400'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AssessmentTopic',
            new_name='QuestionSet',
        ),
    ]
