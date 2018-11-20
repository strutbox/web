FROM python:3.7.1-alpine3.8

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
        g++ \
        gcc \
        libffi-dev \
        linux-headers \
        musl-dev \
        postgresql-dev \
    ; \
    \
    export PIPENV_CACHE_DIR="$(mktemp -d)"; \
    pip install pipenv==2018.11.14; \
    pipenv install --deploy --system; \
    \
    apk del .build-deps; \
    pip uninstall --yes \
        pipenv \
        virtualenv \
        virtualenv-clone \
    ; \
    rm -r "$PIPENV_CACHE_DIR"; \
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
