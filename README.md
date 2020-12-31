# miRNAFinder-web-server

## Nginx configuration
Please replace `URL` in nginx.conf
```
server {
    listen       80 default_server;
    listen       [::]:80 default_server;
    server_name  localhost;
    root         /var/www/html;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/uwsgi.socket;
        uwsgi_read_timeout 1h;
        uwsgi_send_timeout 1h;
    }
```
