#!/usr/bin/env bash
envsubst '\$PORT' < nginx.conf > /etc/nginx/nginx.conf
service nginx start
uwsgi --ini app.ini