FROM python:3.7.2-stretch

RUN DEBIAN_FRONTEND=noninteractive apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y default-jre nginx gettext-base
WORKDIR /app

ADD . /app
ARG PORT=80
RUN echo $PORT
RUN pip install -r requirements.txt
RUN envsubst '\$PORT' < nginx.conf > /etc/nginx/nginx.conf

# Install ViennaRNA
RUN DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends -y ./perl-rna_2.4.17-1_amd64.deb

RUN rm Dockerfile nginx.conf perl-rna_2.4.17-1_amd64.deb requirements.txt
RUN chown -R www-data:www-data /app

RUN chmod +x ./start.sh
CMD ["./start.sh"]