#!/usr/bin/env bash
envsubst '\$PORT' < nginx.conf > /etc/nginx/nginx.conf
service nginx start
nohup redis-stable/src/redis-server &> redis.log &
nohup celery -A app.celery_app worker -B -l info &> celery.log &
uwsgi --ini app.ini
