# Generated by Django 3.2 on 2021-04-10 14:48

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('valid', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='AnswerSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('date', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='AnswerInput',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='answers.answer')),
                ('value', models.CharField(max_length=512)),
            ],
            bases=('answers.answer',),
        ),
        migrations.CreateModel(
            name='AnswerNumberLine',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='answers.answer')),
                ('value', models.IntegerField()),
            ],
            bases=('answers.answer',),
        ),
        migrations.CreateModel(
            name='AnswerSelect',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='answers.answer')),
            ],
            bases=('answers.answer',),
        ),
        migrations.CreateModel(
            name='AnswerSort',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='answers.answer')),
            ],
            bases=('answers.answer',),
        ),
        migrations.CreateModel(
            name='AssessmentTopicAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complete', models.BooleanField(default=True)),
                ('duration', models.DurationField()),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_topic_answers', to='answers.answersession')),
            ],
        ),
    ]
