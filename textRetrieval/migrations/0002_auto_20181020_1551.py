# Generated by Django 2.1.1 on 2018-10-20 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textRetrieval', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='word_original',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='search',
            name='word',
            field=models.TextField(blank=True, null=True),
        ),
    ]
