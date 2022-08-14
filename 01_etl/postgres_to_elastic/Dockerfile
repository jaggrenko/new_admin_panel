FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /migrator
COPY requirements.txt /migrator/

RUN pip install -r requirements.txt --no-cache-dir

COPY . /migrator