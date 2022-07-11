FROM python:3.10-slim

COPY Pipfile .
COPY Pipfile.lock .
COPY requirements.txt .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc cron \
    && python3 -m ensurepip \
    && pip3 install --no-cache --upgrade pip setuptools \
    && pip install pipenv unittest-xml-reporting \
    && pipenv install --system

COPY cron /app/cron
COPY handler.py /app/handler.py
COPY backup.py /app/backup.py
COPY tools /app/tools
COPY templates /app/templates
COPY entrypoint.sh /app/entrypoint.sh

WORKDIR /app/
ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 5000