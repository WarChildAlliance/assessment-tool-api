# Generated by Django 3.2 on 2021-05-31 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0009_auto_20210513_0804'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='file',
            field=models.FileField(null=True, upload_to='attachments'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='link',
            field=models.CharField(blank=True, max_length=2048),
        ),
    ]
