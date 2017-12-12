import click


@click.command()
@click.option('--dev', default=False, is_flag=True)
@click.option('--bind', default='127.0.0.1:8000')
@click.option('--workers', default=1)
def run(dev, bind, workers):
    'Start the webserver.'

    import os
    import sys

    try:
        bind = os.environ['STRUT_BIND']
    except KeyError:
        pass

    dev_options = {
        'py-autoreload': 1,
    }

    options = {
        'auto-procname': True,
        'die-on-term': True,
        'disable-write-exception': True,
        'enable-threads': True,
        'http-socket': bind,
        'ignore-sigpipe': True,
        'ignore-write-errors': True,
        'master': True,
        'module': 'strut.wsgi:application',
        'need-app': True,
        'protocol': 'http',
        'single-interpreter': True,
        'thunder-lock': True,
        'virtualenv': sys.prefix,
        'workers': workers,
    }

    if dev:
        options.update(dev_options)

    for k, v in options.items():
        if v is None:
            continue
        key = 'UWSGI_' + k.upper().replace('-', '_')
        if isinstance(v, str):
            value = v
        elif v is True:
            value = 'true'
        elif v is False:
            value = 'false'
        elif isinstance(v, int):
            value = str(v)
        else:
            raise TypeError('Unknown option type: %r (%s)' % (k, type(v)))

        os.environ[key] = value

    os.execvp('uwsgi', ('uwsgi',))
