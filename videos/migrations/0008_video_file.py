# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-09 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0007_remove_userprofile_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='file',
            field=models.FileField(null=True, upload_to='videos/', verbose_name=''),
        ),
    ]