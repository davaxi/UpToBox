#!/bin/sh

crontab /app/cron/cron.d
service cron start

printenv | grep -v "no_proxy" >> /etc/environment

nginx

gunicorn  handler:app -w 2 --threads 2 -b 0.0.0.0:5000