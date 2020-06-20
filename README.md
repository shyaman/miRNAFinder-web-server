# miRNAFinder-web-server

## Nginx configuration
Please replace `URL`
```
server {

    listen 80;
    listen [::]:80;
    server_name URL;

    location / {
        include uwsgi_params;
        uwsgi_read_timeout 1h;
        uwsgi_send_timeout 1h;
        uwsgi_pass mirnafinderapp:8080;
    }

}
```
