# Generated by Django 4.0.5 on 2022-11-29 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('answers', '0019_alter_questionsetanswer_session_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionsetanswer',
            old_name='topic_access',
            new_name='question_set_access',
        ),
    ]
