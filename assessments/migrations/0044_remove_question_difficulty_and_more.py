# Generated by Django 4.0.5 on 2022-10-25 07:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0043_auto_20221010_0912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='difficulty',
        ),
        migrations.AddField(
            model_name='question',
            name='learning_objective',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='assessments.learningobjective'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='subject',
            field=models.CharField(choices=[('MATH', 'Math'), ('LITERACY', 'Literacy'), ('TUTORIAL', 'Tutorial')], max_length=32),
        ),
        migrations.AlterField(
            model_name='subtopic',
            name='subject',
            field=models.CharField(choices=[('MATH', 'Math'), ('LITERACY', 'Literacy'), ('TUTORIAL', 'Tutorial')], max_length=32),
        ),
    ]
