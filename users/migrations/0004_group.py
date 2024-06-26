# Generated by Django 3.2 on 2022-05-17 12:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_language_direction'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Group name')),
                ('supervisor', models.ForeignKey(limit_choices_to={'role': 'SUPERVISOR'}, on_delete=django.db.models.deletion.CASCADE, related_name='group_supervisor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_group', to='users.group'),
        ),
    ]
