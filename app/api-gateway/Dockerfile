ARG PLATFORM=arm64

# Debian 기반 빌드 단계
FROM arm64v8/python:3.12-slim AS arm64

# Alpine 기반 빌드 단계
FROM python:3.12-slim AS amd64

FROM ${PLATFORM} AS final

LABEL maintainer="miraclehand@naver.com"
WORKDIR /app

COPY requirements.txt ./
COPY packages /app/packages

RUN pip install --no-index --find-links=/app/packages -r requirements.txt

COPY ./src /app/src
COPY .pylintrc ./
COPY .env ./

CMD ["sh", "-c", "pylint src/*.py && python src/app.py"]
