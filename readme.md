# NewsScorer

## Simple News parser and sentiment analyser with Django + Redis + Celery + Tensorflow + Huggingface NLP model

### Introduction
This django system can parse news websites, including Finviz, Reuters and WSJ, and store data into PostgresDB.

These data then passed to NLP model (cardiffnlp/twitter-roberta-base-sentiment) with customized model weight (nlp_package) to obtain sentiment score (0: negative, 1:neutral, 2:positive)

Here is the process flow:
1. News parsing (finished at celery worker)
2. Data uploading (finished at celery worker)
3. Sentiment Prediction (finished at celery tf worker)

If you are first time to use Django, you may check the reference part first.

### Installation
1. Add .env in /news_scorer/news_scorer/env folder, and change DJANGO_SECRET_KEY and POSTGRES info
```BROKER_TYPE=REDIS
CELERY_BROKER_URL_REDIS=redis://redis:6379/1
DJANGO_SECRET_KEY=""
POSTGRES_DB=news_grabber
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_pw
POSTGRES_HOST=db
POSTGRES_PORT=5432
LOCAL_TZ_STR=Asia/Hong_Kong
DJANGO_SECRET_KEY={pls replace this}
```
2. Download nlp_package content to /news_scorer/news_scorer/nlp_package
   Link: https://drive.google.com/file/d/1-O3PvgQ4iJnPKuSt7NHwuO5bSmNJhioB/view?usp=sharing
2. docker-compose up -d --build
3. docker exec -it news_scorer-web-1 python3 manage.py migrate
4. docker exec -it news_scorer-web-1 python3 manage.py createsuperuser
5. docker exec -it news_scorer-web-1 python3 news_scorer/run_after_migration.py
6. Restart all service


### Future possible enhancement

- Improve WSF parser
- Add more parser
- Add production settings
- API development
- etc...

### Reference

- Django Documents
- Celery Documents 
- Tensorflow Documents
- Huggingface Documents
  - https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment