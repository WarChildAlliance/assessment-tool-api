# Generated by Django 4.0.5 on 2022-07-18 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_active_status_updated_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='active_status_updated_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]