FROM python:3.6.3-alpine

RUN addgroup -S strut && adduser -S -G strut strut

ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

RUN apk add --no-cache 'su-exec>=0.2'

RUN mkdir -p /usr/src/strut
WORKDIR /usr/src/strut

COPY requirements-base.txt /usr/src/strut/
RUN set -ex; \
    \
    apk add --no-cache --virtual .build-deps \
        gcc \
        linux-headers \
        musl-dev \
        postgresql-dev \
    ; \
    \
    pip install -r requirements-base.txt; \
    \
    apk del .build-deps; \
    \
    apk add --no-cache --virtual .run-deps \
        libpq \
    ;

COPY requirements.txt /usr/src/strut/
RUN pip install -r requirements.txt

COPY . /usr/src/strut
RUN pip install -e . && strut-web --help

ENTRYPOINT ["/usr/src/strut/docker-entrypoint.sh"]

EXPOSE 8000

ENV STRUT_BIND 0.0.0.0:8000
CMD ["strut-web"]
