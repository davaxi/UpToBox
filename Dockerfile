FROM python:3.10-alpine3.16

COPY Pipfile .
COPY Pipfile.lock .
COPY requirements.txt .

RUN apk add --update --no-cache python3 postgresql-dev gcc musl-dev linux-headers g++ python3-dev   \
    && ln -sf python3 /usr/bin/python \
    && python3 -m ensurepip \
    && pip3 install --no-cache --upgrade pip setuptools \
    && pip install pipenv unittest-xml-reporting \
    && pipenv install --system