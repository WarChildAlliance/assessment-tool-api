# Generated by Django 4.0.5 on 2022-12-06 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0049_merge_20221202_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
