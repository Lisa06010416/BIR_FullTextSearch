# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Search(models.Model):
    word = models.TextField(blank=True, null=True)
    word_original = models.TextField(blank=True, null=True)
    countallfiles = models.IntegerField()
    countpudmedfiles = models.IntegerField()
    counttwitterfiles = models.IntegerField()
    fileindex = models.TextField()

    class Meta:
        managed = True
        db_table = 'search'


class Text(models.Model):
    fileindex = models.IntegerField(blank=True, null=True)
    filetype = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    sentencenum = models.IntegerField()
    wordnum = models.IntegerField()
    characternum = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'text'
