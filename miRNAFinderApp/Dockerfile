FROM python:3.7.2-stretch

RUN DEBIAN_FRONTEND=noninteractive apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y default-jre
WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

# Install ViennaRNA
ADD https://www.tbi.univie.ac.at/RNA/download/debian/debian_9_0/perl-rna_2.4.14-1_amd64.deb .
RUN DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends -y ./perl-rna_2.4.14-1_amd64.deb && rm perl-rna_2.4.14-1_amd64.deb

CMD ["uwsgi", "app.ini"]