FROM python:3.7.3-alpine3.8

RUN addgroup -S strut && adduser -S -G strut strut

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1

RUN apk add --no-cache 'su-exec>=0.2'

RUN mkdir -p /usr/src/strut
WORKDIR /usr/src/strut

RUN set -ex; \
    \
    apk add --no-cache \
        ffmpeg

COPY . /usr/src/strut

RUN set -ex; \
    \
    apk add --no-cache --virtual .build-deps \
        curl \
        g++ \
        gcc \
        libffi-dev \
        linux-headers \
        musl-dev \
        postgresql-dev \
    ; \
    \
    export POETRY_VERSION=0.12.16; \
    curl -sSL https://raw.githubusercontent.com/sdispater/poetry/$POETRY_VERSION/get-poetry.py | python; \
    ~/.poetry/bin/poetry config settings.virtualenvs.create false; \
    ~/.poetry/bin/poetry install --no-dev; \
    rm -r ~/.poetry ~/.config; \
    \
    apk del .build-deps; \
    \
    apk add --no-cache --virtual .run-deps \
        libffi \
        libpq \
        libstdc++ \
    ; \
    strut --help

ARG BUILD_REVISION
ENV BUILD_REVISION $BUILD_REVISION

ENTRYPOINT ["/usr/src/strut/docker-entrypoint.sh"]
EXPOSE 8000

ENV STRUT_BIND 0.0.0.0:8000
CMD ["strut"]
