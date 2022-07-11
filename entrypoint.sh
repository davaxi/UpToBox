#!/bin/sh

crontab /app/cron/cron.d
service cron start

gunicorn  handler:app -w 2 --threads 2 -b 0.0.0.0:5000