# Generated by Django 4.0.5 on 2022-07-08 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0029_merge_20220714_1508'),
        ('answers', '0009_delete_answerdraganddrop'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerDragAndDrop',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='answers.answer')),
            ],
            bases=('answers.answer',),
        ),
        migrations.CreateModel(
            name='DragAndDropAreaEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='answers.answerdraganddrop')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='assessments.areaoption')),
                ('selected_draggable_options', models.ManyToManyField(blank=True, to='assessments.draggableoption')),
            ],
        ),
    ]
