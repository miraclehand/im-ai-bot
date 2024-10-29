ARG PLATFORM=arm64

# Debian 기반 빌드 단계
FROM arm64v8/python:3.12-slim AS arm64

# Alpine 기반 빌드 단계
FROM python:3.12-slim AS amd64

FROM ${PLATFORM} AS final

LABEL maintainer="miraclehand@naver.com"
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends g++ make && rm -rf /var/lib/apt/lists/* && apt-get clean

#COPY ./models /app/models

COPY requirements.txt ./
COPY packages /app/packages

RUN pip install --no-index --find-links=/app/packages -r requirements.txt

COPY ./src /app/src
COPY .env ./
COPY .pylintrc ./

ENV PYTHONPATH=/app/src

CMD ["sh", "-c", "find ./src -name '*.py' -exec pylint {} \\; && gunicorn --timeout 6000 -w 1 -b 0.0.0.0:8080 --log-level info --access-logfile - --error-logfile - 'src.app:create_app()'"]
