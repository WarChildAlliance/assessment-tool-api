# Generated by Django 4.0.5 on 2022-12-05 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0052_remove_questionsetaccess_unique_access_per_student_and_topic_and_more'),
        ('gamification', '0012_rename_topic_topiccompetency_question_set'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TopicCompetency',
            new_name='QuestionSetCompetency',
        ),
        migrations.AlterModelOptions(
            name='questionsetcompetency',
            options={'verbose_name_plural': 'QuestionSet competencies'},
        ),
    ]
