# Generated by Django 3.0.2 on 2020-01-10 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league_history', '0002_matchups'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProTeam',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('location', models.CharField(max_length=64, null=True)),
                ('name', models.CharField(max_length=64, null=True)),
                ('abbrev', models.CharField(max_length=64)),
            ],
            options={
                'unique_together': {('location', 'name')},
            },
        ),
    ]
