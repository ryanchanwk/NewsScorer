# Generated by Django 3.2.7 on 2021-09-14 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news_store', '0010_auto_20210912_1125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsstore',
            name='sentiment_data',
        ),
    ]