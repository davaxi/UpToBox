FROM node:16-alpine3.16

ENV LANG="fr_FR.UTF-8"

COPY Pipfile .
COPY Pipfile.lock .
COPY requirements.txt .

RUN apk add --update --no-cache python3 gcc musl-dev linux-headers g++ python3-dev  \
    && ln -sf python3 /usr/bin/python \
    && python3 -m ensurepip \
    && pip3 install --no-cache --upgrade pip setuptools \
    && pip install pipenv unittest-xml-reporting \
    && pipenv install --system