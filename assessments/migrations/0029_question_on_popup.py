# Generated by Django 3.2 on 2022-06-24 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0028_auto_20220613_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='on_popup',
            field=models.BooleanField(default=False),
        ),
    ]
