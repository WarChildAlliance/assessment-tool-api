# Generated by Django 4.0.5 on 2023-01-06 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0060_remove_questionnumberline_shuffle_question_shuffle'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionsetaccess',
            name='created_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='questionsetaccess',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
    ]