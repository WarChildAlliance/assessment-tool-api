# Generated by Django 4.0.5 on 2023-01-03 08:55

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_rename_student_grade_user_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='skip_intro_for_assessments',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
    ]