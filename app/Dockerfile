####################### BASE IMAGE #######################

FROM python:3.12-slim AS base

EXPOSE 80

WORKDIR /srv/app

RUN apt-get clean \
    && apt-get -y update \
    && apt-get -y install \
    build-essential \
    python3-dev \
    weasyprint \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --src /usr/local/src \
    && apt-get -y remove \
    build-essential \
    python3-dev

####################### DEV IMAGE ########################

FROM base AS development

# source code is not copied because it is supposed to be
# bind mounted as a volume.

CMD [ "flask", "--app", "main", "run", "--host", "0.0.0.0", "--port", "80", "--debug" ]

####################### PROD IMAGE #######################

FROM base AS production

COPY . .

CMD [ "flask", "--app", "main", "run", "--host", "0.0.0.0", "--port", "80" ]