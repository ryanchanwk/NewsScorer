# Generated by Django 3.2.7 on 2021-10-13 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news_store', '0016_auto_20211013_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newssourcetag',
            name='news_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='news_store.newssource', unique=True),
        ),
        migrations.AlterField(
            model_name='newssourcetag',
            name='tag',
            field=models.CharField(blank=True, max_length=256, null=True, unique=True),
        ),
    ]
