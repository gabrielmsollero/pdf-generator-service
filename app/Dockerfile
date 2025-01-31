######################## BASE IMAGE #######################

FROM python:3.12-slim AS base

EXPOSE 80

RUN groupadd --gid 1000 python && \
    useradd --uid 1000 --gid python --shell /bin/bash --create-home python

RUN apt-get clean \
    && apt-get -y update \
    && apt-get -y install \
    weasyprint \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

USER python

WORKDIR /home/python/app

ENV PATH=/home/python/.local/bin:$PATH
ENV PYTHONPATH=/home/python/.local/lib/python3.12/site-packages:$PYTHONPATH

COPY --chown=python:python requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

####################### DEV IMAGE #########################

FROM base AS development

# source code is not copied because it is supposed to be
# bind mounted as a volume.

CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "80", "--debug" ]

####################### PROD IMAGE ########################

FROM base AS production

ENV ENVIRONMENT=production

USER root

RUN apt-get clean \
    && apt-get -y update \
    && apt-get -y install nginx=1.22.* sudo \
    && rm -rf /var/lib/apt/lists/* \
    && echo "python ALL=(ALL) NOPASSWD: /usr/sbin/service nginx start" \
    >> /etc/sudoers

COPY --chown=python:python . .

RUN mv ./deployment/nginx.conf /etc/nginx/ \
    && chmod +x ./deployment/start.sh

USER python

CMD [ "./deployment/start.sh" ]