#!/bin/sh

if [ "${1#-}" != "$1" ] ; then
  set -- strut "$@"
fi

if strut "$1" --help > /dev/null 2>&1; then
  set -- strut "$@"
fi

if [ "$1" = 'strut' -a "$(id -u)" = '0' ]; then
  exec su-exec strut "$0" "$@"
fi

exec "$@"
