# Generated by Django 3.2.7 on 2021-09-10 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_store', '0007_newssource_parent_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsstore',
            name='sentiment_data',
            field=models.ManyToManyField(blank=True, to='news_store.SentimentStore'),
        ),
    ]