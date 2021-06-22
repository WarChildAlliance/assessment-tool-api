# Generated by Django 3.2 on 2021-06-16 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0012_merge_20210602_0744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='subject',
            field=models.CharField(choices=[('MATH', 'Math'), ('LITERACY', 'Literacy'), ('PRESEL', 'PreSel'), ('POSTSEL', 'PostSel')], max_length=32),
        ),
    ]
