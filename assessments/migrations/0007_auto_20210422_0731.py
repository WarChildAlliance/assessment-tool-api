# Generated by Django 3.2 on 2021-04-22 07:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0006_assessmenttopicaccess_unique_access_per_student_and_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmenttopic',
            name='description',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='assessments.assessmenttopic'),
        ),
    ]
