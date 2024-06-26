# Generated by Django 3.2 on 2021-06-28 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0002_alter_topiccompetency_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(null=True, upload_to='avatars')),
                ('effort_cost', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='avatars_collection',
            field=models.ManyToManyField(to='gamification.Avatar'),
        ),
    ]
