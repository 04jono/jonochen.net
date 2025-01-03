# Generated by Django 5.0.1 on 2024-04-19 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('song_name', models.CharField(max_length=255, verbose_name='Song Name')),
                ('artist', models.CharField(max_length=255, verbose_name='Artist')),
                ('release_year', models.CharField(max_length=255, verbose_name='Release Year')),
                ('album_url', models.CharField(max_length=255, verbose_name='Album URL')),
                ('database_uri', models.CharField(max_length=255, verbose_name='Database URI')),
                ('playlist', models.CharField(max_length=255, verbose_name='Playlist')),
                ('song_identifier', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Song Identifier')),
            ],
        ),
        migrations.CreateModel(
            name='SongOfDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateField(auto_now_add=True, verbose_name='Date Added')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playlistle.song')),
            ],
        ),
    ]
