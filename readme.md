1. docker-compose up -d --build
2. docker exec -it news_scorer-web-1 python3 manage.py migrate
3. docker exec -it news_scorer-web-1 python3 manage.py createsuperuser
4. docker exec -it news_scorer-web-1 python3 run_after_migration.py
5. Restart all service