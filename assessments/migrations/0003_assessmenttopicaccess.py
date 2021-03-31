# Generated by Django 3.1.7 on 2021-03-31 12:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assessments', '0002_auto_20210325_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentTopicAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('student', models.ForeignKey(limit_choices_to={'role': 'STUDENT'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessments.assessmenttopic')),
            ],
            options={
                'verbose_name_plural': 'Assessment topics access',
            },
        ),
    ]
