import fnmatch
import json
import logging
import os
import pickle
import shutil
import uuid

import numpy as np
import pandas as pd
from celery import shared_task
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone
from transformers import AutoTokenizer
from transformers import TFAutoModelForSequenceClassification

from .models import NewsSource
from .models import SentimentSource, SentimentStore, NewsStore, NewsSourceTag
from .parser.map import PARSER_MAP
from .tf_tasks import dataset_generator, array_generator

logger = logging.getLogger(__name__)

import sys
sys.setrecursionlimit(10000)


@shared_task(name='dummy_task')
def dummy_task(a, b):
    return a + b


@shared_task(name='parse_news')
def parse_news(name: str):
    uuid_str = str(uuid.uuid4())
    news_source = NewsSource.objects.get(source_name=name)
    parser = PARSER_MAP[name]
    news_source_parser = parser(news_source)
    parsed_data = news_source_parser.run()
    with open(f'/{settings.BASE_DIR}/temp_store/{news_source.id}-{uuid_str}.pickle', 'wb') as handle:
        pickle.dump(parsed_data, handle)
    logger.info(f'{len(parsed_data)} data are dumped.')


@shared_task(name='news_uploader', bind=True)
def news_uploader(self):
    pattern = '*.pickle'
    file_list = [file for file in os.listdir(f'/{settings.BASE_DIR}/temp_store') if fnmatch.fnmatch(file, pattern)]

    for file in file_list:
        with open(os.path.join(f'/{settings.BASE_DIR}/temp_store', file), 'rb') as handle:
            data = pickle.load(handle)
        new_source_num, _ = file.split('-', 1)
        news_source = NewsSource.objects.get(pk=int(new_source_num))

        time_ago = timezone.now() - timezone.timedelta(hours=36)
        qs = NewsStore.objects.filter(news_source=news_source, news_datetime__gt=time_ago)
        exist_url = list(qs.values_list('news_url', flat=True))
        df = pd.DataFrame.from_dict(data, orient='index')
        df = df[~df.index.isin(exist_url)].copy()
        for index, row in df.iterrows():
            try:
                news_source_tag = None
                if news_source.enable_tag is True:
                    if row.get('article_tag'):
                        if row.article_tag is not None:
                            news_source_tag = NewsSourceTag.get_or_create_news_source_tag(news_source, row.article_tag)

                news = NewsStore.objects.create(title=row.title, body=row.body, news_url=index, news_source=news_source,
                                                news_datetime=row.datetime, execution_batch=self.request.id,
                                                news_source_tag=news_source_tag)
                news.update_actual_news_store()
            except IntegrityError:
                logger.error(f'news_store {row.title} {index} cannot be added because duplication')
                continue

        logger.info(f'data are uploaded to db.')
        shutil.copyfile(os.path.join(f'/{settings.BASE_DIR}/temp_store', file),
                        os.path.join(f'/{settings.BASE_DIR}/archive', file))
        os.remove(os.path.join(f'/{settings.BASE_DIR}/temp_store', file))


@shared_task(name='single_tf_predict')
def main(source_name):
    sentiment_source = SentimentSource.objects.filter(source_name=source_name)
    if sentiment_source.count() == 0:
        return
    else:
        sentiment_source = sentiment_source.first()
    logger.info(f"Reading json {sentiment_source.config_path}")
    news_store = NewsStore.objects.all()
    sentiment_store = SentimentStore.objects.filter(sentiment_source=sentiment_source, news_store__in=news_store)
    news_store_need_process = news_store.exclude(id__in=list(sentiment_store.values_list('news_store__id', flat=True)))
    with open(sentiment_source.config_path) as file:
        config = json.load(file)
        BATCH_SIZE = config.get("BATCH_SIZE")
        CASED = config.get("CASED")

    logger.info(f"Reading testing data, count: {news_store_need_process.count()}")
    testing_sentence_array, _ = array_generator(news_store_need_process, CASED)

    if len(testing_sentence_array) == 0:
        logger.info(f"No data is predicted")
        return

    logger.info(f"Initializing tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(sentiment_source.token_model_name)
    logger.info(f"Creating training ds...")
    test_tfds = dataset_generator(tokenizer, testing_sentence_array, BATCH_SIZE)
    logger.info(f"Initializing pretrain model...")
    if (sentiment_source.pretrain_model_path is None) or (config is None):
        model = TFAutoModelForSequenceClassification.from_pretrained(sentiment_source.token_model_name)
    else:
        model = TFAutoModelForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=sentiment_source.pretrain_model_path,
            config=sentiment_source.pretrain_model_config_path)
    logger.info(f"Loading model weights...")
    model.load_weights(sentiment_source.weight_path)
    raw_predicted_result = model.predict(test_tfds)
    logit_predicted_result = raw_predicted_result.logits
    # print(logit_predicted_result.shape)
    argmax_predicted_result = np.argmax(logit_predicted_result, axis=1)
    # print(argmax_predicted_result)
    # print(raw_predicted_result.logits)
    assert len(logit_predicted_result) == len(argmax_predicted_result)
    assert len(argmax_predicted_result) == len(testing_sentence_array)
    assert len(testing_sentence_array) == len(news_store_need_process)
    output = []
    for i in range(len(logit_predicted_result)):
        output.append({'predicted_class': argmax_predicted_result[i], 'other_result': logit_predicted_result[i],
                       'predicted_text': testing_sentence_array[i]})

    for i in range(len(output)):
        try:
            SentimentStore.objects.create(news_store=news_store_need_process[i], sentiment_source=sentiment_source,
                                          predicted_text=output[i]['predicted_text'],
                                          predicted_class=int(output[i]['predicted_class']),
                                          other_result=output[i]['other_result'])
        except:
            logger.error(f'news_store {news_store} cannot be added', exc_info=True)
            continue
