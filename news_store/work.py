# Shell Plus Model Imports
# Shell Plus Django Imports
import datetime
import pytz
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_grabber.settings')
import django
django.setup()

# from django.db.models import Avg, Sum
#
# from news_store.models import NewsStore, SentimentStore
#
# timezone_str = 'US/Eastern'
# # timezone_str = 'Asia/Hong_Kong'
# source_timezone = pytz.timezone(timezone_str)
#
# start_date = datetime.datetime(2021, 10, 1, 0, 0, 0, tzinfo=source_timezone)
# end_date = datetime.datetime(2021, 10, 30, 0, 0, 0, tzinfo=source_timezone)
# delta = datetime.timedelta(minutes=1)
#
# while start_date <= end_date:
#     news_source_last = NewsStore.objects.filter(news_datetime__lt=start_date).order_by('-news_datetime',
#                                                                                        '-create_datetime')[:30]
#     # score = SentimentStore.objects.filter(news_store__in=news_source_last).aggregate(Avg('predicted_class'))
#     # print(f"{start_date.date()}@{start_date.time()}@{score['predicted_class__avg']}")
#     score = SentimentStore.objects.filter(news_store__in=news_source_last).aggregate(Sum('predicted_class'))
#     print(f"{start_date.date()} {start_date.time()}@{score['predicted_class__sum']}")
#     start_date += delta


from news_store.tasks import parse_news
parse_news('Finviz')
