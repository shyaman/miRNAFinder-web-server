#!/usr/bin/env bash
envsubst '\$PORT' < nginx.conf > /etc/nginx/nginx.conf
service nginx start
./run-redis.sh
celery -A app.celery_app worker -B -l info &
uwsgi --ini app.ini
