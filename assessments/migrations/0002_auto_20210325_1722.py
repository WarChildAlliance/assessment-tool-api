# Generated by Django 3.1.7 on 2021-03-25 17:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='created_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'SUPERVISOR'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
