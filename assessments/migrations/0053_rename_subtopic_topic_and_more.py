# Generated by Django 4.0.5 on 2022-12-05 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0052_remove_questionsetaccess_unique_access_per_student_and_topic_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subtopic',
            new_name='Topic',
        ),
        migrations.RenameField(
            model_name='assessment',
            old_name='subtopic',
            new_name='topic',
        ),
        migrations.RenameField(
            model_name='learningobjective',
            old_name='subtopic',
            new_name='topic',
        ),
    ]
