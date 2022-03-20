import os
import dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_grabber.settings')

import django

django.setup()

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from news_store.models import NewsSource, NewsStore, SentimentStore, SentimentSource, NewsSourceTag

LOCAL_TZ_STR = os.environ.get('LOCAL_TZ_STR', '')


def delete_all_news_sentiment_data():
    SentimentStore.objects.all().delete()
    SentimentSource.objects.all().delete()
    NewsStore.objects.all().delete()
    NewsSourceTag.objects.all().delete()
    NewsSource.objects.all().delete()
    PeriodicTask.objects.exclude(name='celery.backend_cleanup').delete()
    print("finish delete all news and sentiment data. ")


def create_news_sources():
    single_news_sources = [
        NewsSource(source_name="BigMaker", source_url="https://www.bigmarker.com/", parent_url="bigmarker.com"),
        NewsSource(source_name="CNN-IT", source_url="https://cnn.it/", parent_url="cnn.it"),
        NewsSource(source_name="CNBC", source_url="https://www.cnbc.com/", parent_url="cnbc.com"),
        NewsSource(source_name="MarketWatch", source_url="http://feeds.marketwatch.com/", parent_url="marketwatch.com"),
        NewsSource(source_name="BBC_UK", source_url="https://www.bbc.co.uk/news/", parent_url="bbc.co.uk"),
        NewsSource(source_name="NYtime", source_url="https://www.nytimes.com/", parent_url="nytimes.com"),
        NewsSource(source_name="CNN", source_url="https://edition.cnn.com/", parent_url="cnn.com",
                   source_timezone=LOCAL_TZ_STR),
        NewsSource(source_name="Fox_Business", source_url="https://www.foxbusiness.com/markets/",
                   parent_url="foxbusiness.com"),
        NewsSource(source_name="Bloomberg", source_url="https://www.bloomberg.com/",
                   parent_url="bloomberg.com", source_timezone=LOCAL_TZ_STR),
        NewsSource(source_name="Yahoo_Finance", source_url="https://finance.yahoo.com/", parent_url="finance.yahoo.com",
                   source_timezone=LOCAL_TZ_STR, is_integrate_source=True),
        NewsSource(source_name="WSJ", source_url="https://www.wsj.com/news/latest-headlines?mod=wsjheader",
                   parent_url="wsj.com", enable_tag=True),
        NewsSource(source_name="Reuters", source_url="https://www.reuters.com/news/archive/marketsNews?view=page",
                   parent_url="reuters.com"),
        NewsSource(source_name="Finviz", source_url="https://finviz.com/news.ashx", parent_url="US/Eastern",
                   is_integrate_source=True)
    ]
    NewsSource.objects.bulk_create(single_news_sources)
    NewsSource.objects.get(source_name="Finviz").excluded_source.add(NewsSource.objects.get(source_name="WSJ"))
    NewsSource.objects.get(source_name="Finviz").excluded_source.add(NewsSource.objects.get(source_name="Reuters"))
    print("finish create_news_sources. ")


def create_sentiment_source():
    SentimentSource.objects.create(source_name="cardiffnlp-twitter-roberta-finetune-news",
                                   token_model_name="cardiffnlp/twitter-roberta-base-sentiment",
                                   config_path="/usr/src/app/news_scorer/nlp_package/cardiffnlp-twitter-roberta-base-sentiment.json",
                                   weight_path="/usr/src/app/news_scorer/nlp_package/customized_cardiffnlp-twitter-roberta-base-sentiment.h5"
                                   )
    print("finish create_sentiment_source. ")


def create_periodic_task():
    parse_cron = CrontabSchedule.objects.create(minute="0,15,30,45", timezone=LOCAL_TZ_STR)
    upload_cron = CrontabSchedule.objects.create(minute="5,20,35,50", timezone=LOCAL_TZ_STR)
    predict_cron = CrontabSchedule.objects.create(minute="10,25,40,55", timezone=LOCAL_TZ_STR)

    tasks = [PeriodicTask(name='parse_news_wsj', task='parse_news', crontab=parse_cron, kwargs='{"name":"WSJ"}',
                           queue='normal',
                           exchange='normal', routing_key='normal', priority=1, expire_seconds=120),
             PeriodicTask(name='parse_news_reuters', task='parse_news', crontab=parse_cron,
                           kwargs='{"name":"Reuters"}',
                           queue='normal',
                           exchange='normal', routing_key='normal', priority=1, expire_seconds=120),
             PeriodicTask(name='parse_news_finviz', task='parse_news', crontab=parse_cron, kwargs='{"name":"Finviz"}',
                           queue='normal',
                           exchange='normal', routing_key='normal', priority=1, expire_seconds=120),
             PeriodicTask(name='news_uploader', task='news_uploader', crontab=upload_cron, queue='normal',
                           exchange='normal', routing_key='normal', priority=1, expire_seconds=120),
             PeriodicTask(name='model_run', task='single_tf_predict', crontab=predict_cron,
                           kwargs='{"source_name":"cardiffnlp-twitter-roberta-finetune-news"}', queue='tf',
                           exchange='tf', routing_key='tf', priority=1, expire_seconds=120)]
    PeriodicTask.objects.bulk_create(tasks)
    print("finish create_periodic_task. ")


if __name__ == '__main__':
    delete_all_news_sentiment_data()
    create_news_sources()
    create_sentiment_source()
    create_periodic_task()
