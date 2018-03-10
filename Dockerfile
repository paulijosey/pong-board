FROM python:3.6-slim

WORKDIR /code

ADD . /code

RUN pip install -r requirements.txt