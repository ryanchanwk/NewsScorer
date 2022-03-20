# pull official base image
FROM python:3.8.12-slim

# set work directory
WORKDIR /usr/src/app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y \
    postgresql-server-dev-all \
    gcc \
    python3-dev \
    musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./news_scorer/requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .