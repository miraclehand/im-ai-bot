FROM arm64v8/python:3.12-slim

LABEL maintainer="miraclehand@naver.com"

WORKDIR /app

COPY requirements.txt ./
COPY packages /app/packages

# 필요한 패키지를 설치합니다
#RUN apk update && apk add --no-cache g++ make
RUN apt update && apt install -y g++ make

RUN pip install --no-index --find-links=/app/packages -r requirements.txt

COPY ./src /app/src
COPY .env ./
COPY .pylintrc ./

ENV PYTHONPATH=/app/src

CMD find ./src -name '*.py' -exec pylint {} \; && gunicorn --timeout 6000 -w 1 -b 0.0.0.0:8080 --log-level info --access-logfile - --error-logfile - "src.app:create_app()"

