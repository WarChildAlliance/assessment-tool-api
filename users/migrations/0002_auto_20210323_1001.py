# Generated by Django 3.1.7 on 2021-03-23 10:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name_en', models.CharField(max_length=100)),
                ('name_local', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='created_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'SUPERVISOR'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name_en', models.CharField(max_length=100)),
                ('name_local', models.CharField(blank=True, max_length=100, null=True)),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.language')),
            ],
        ),
    ]
