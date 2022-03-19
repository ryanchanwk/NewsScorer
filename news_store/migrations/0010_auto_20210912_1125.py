# Generated by Django 3.2.7 on 2021-09-12 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_store', '0009_auto_20210911_2348'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sentimentstore',
            old_name='predicted_result',
            new_name='predicted_class',
        ),
        migrations.AddField(
            model_name='sentimentstore',
            name='other_result',
            field=models.CharField(default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sentimentstore',
            name='predicted_text',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='sentimentstore',
            name='remark',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]