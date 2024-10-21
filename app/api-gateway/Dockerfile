FROM arm64v8/python:3.12-slim

LABEL maintainer="miraclehand@naver.com"

WORKDIR /app

COPY requirements.txt ./
#COPY packages /app/packages

RUN pip install -r requirements.txt
#RUN pip install --no-index --find-links=/app/packages -r requirements.txt

COPY ./src /app/src
COPY .pylintrc ./
COPY .env ./

CMD ["sh", "-c", "pylint **/*.py && python src/app.py"]
