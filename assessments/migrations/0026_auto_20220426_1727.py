# Generated by Django 3.2 on 2022-04-26 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0025_auto_20220415_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessmenttopic',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='selectoption',
            name='value',
            field=models.CharField(default='select-option-value-missing', max_length=256),
        ),
    ]