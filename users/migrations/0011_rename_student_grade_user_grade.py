# Generated by Django 4.0.5 on 2022-10-21 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_merge_0009_user_see_intro_0009_user_student_grade'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='student_grade',
            new_name='grade',
        ),
    ]
