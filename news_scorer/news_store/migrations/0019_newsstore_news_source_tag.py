# Generated by Django 3.2.7 on 2021-10-13 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news_store', '0018_auto_20211013_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsstore',
            name='news_source_tag',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='news_store.newssourcetag'),
        ),
    ]