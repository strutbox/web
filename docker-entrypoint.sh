#!/bin/sh

if [ "${1#-}" != "$1" ] ; then
  set -- strut-web "$@"
fi

if strut-web "$1" --help > /dev/null 2>&1; then
    set -- strut-web "$@"
fi

if [ "$1" = 'strut-web' -a "$(id -u)" = '0' ]; then
    exec su-exec strut "$0" "$@"
fi

exec "$@"
