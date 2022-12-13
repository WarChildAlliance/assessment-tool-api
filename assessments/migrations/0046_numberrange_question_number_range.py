# Generated by Django 4.0.5 on 2022-11-17 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0045_merge_20221107_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(max_length=32)),
                ('min', models.PositiveSmallIntegerField(default=1)),
                ('max', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='number_range',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='assessments.numberrange'),
        ),
    ]