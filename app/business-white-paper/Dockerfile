FROM arm64v8/python:3.12-slim

LABEL maintainer="miraclehand@naver.com"

WORKDIR /app

#COPY ./models /app/models

# 필요한 패키지를 설치합니다
RUN apt-get update && apt-get install -y --no-install-recommends g++ make && rm -rf /var/lib/apt/lists/* && apt-get clean

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY ./src /app/src
COPY .env ./
COPY .pylintrc ./

ENV PYTHONPATH=/app/src

CMD ["sh", "-c", "find ./src -name '*.py' -exec pylint {} \\; && gunicorn --timeout 6000 -w 1 -b 0.0.0.0:8080 --log-level info --access-logfile - --error-logfile - 'src.app:create_app()'"]



