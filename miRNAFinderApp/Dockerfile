FROM python:3.7.2-stretch

RUN DEBIAN_FRONTEND=noninteractive apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y default-jre nginx
WORKDIR /app

ADD . /app
ENV PORT=80
RUN echo $PORT
RUN pip install -r requirements.txt
COPY nginx.conf /etc/nginx
CMD sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/nginx.conf && nginx -g 'daemon off;'

# Install ViennaRNA
RUN DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends -y ./perl-rna_2.4.17-1_amd64.deb

RUN rm Dockerfile perl-rna_2.4.17-1_amd64.deb nginx.conf requirements.txt
RUN chown -R www-data:www-data /app

RUN chmod +x ./start.sh
CMD ["./start.sh"]