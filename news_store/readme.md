docker-compose up -d --build
docker exec -it news_scorer-websource-1 python3 manage.py migrate
docker exec -it news_scorer-websource-1 python3 manage.py createsuperuser