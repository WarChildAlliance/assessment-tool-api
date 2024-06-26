# Generated by Django 3.2 on 2021-04-10 14:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assessments', '0001_initial'),
        ('answers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmenttopicanswer',
            name='topic_access',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_topic_answers', to='assessments.assessmenttopicaccess'),
        ),
        migrations.AddField(
            model_name='answersession',
            name='student',
            field=models.ForeignKey(limit_choices_to={'role': 'STUDENT'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessments.question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='topic_answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='answers.assessmenttopicanswer'),
        ),
        migrations.AddField(
            model_name='answersort',
            name='category_A',
            field=models.ManyToManyField(related_name='answer_category_A', to='assessments.SortOption'),
        ),
        migrations.AddField(
            model_name='answersort',
            name='category_B',
            field=models.ManyToManyField(related_name='answer_category_B', to='assessments.SortOption'),
        ),
        migrations.AddField(
            model_name='answerselect',
            name='selected_options',
            field=models.ManyToManyField(to='assessments.SelectOption'),
        ),
    ]
