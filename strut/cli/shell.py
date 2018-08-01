import click


@click.command()
def shell():
    "Start interactive python shell."


    import strut

    strut.setup()

    import os
    import sys
    import requests
    from django.conf import settings
    from django.db import connection
    from django.db.models import Model

    from strut.db.utils import last_query, explain

    py_version = lambda: sys.version.split('\n', 1)[0]

    banner = f"""\
   _____________  __  ________
  / __/_  __/ _ \/ / / /_  __/
 _\ \  / / / , _/ /_/ / / /
/___/ /_/ /_/|_|\____/ /_/

Python {py_version()}
"""

    # Preload things we will always use
    context = {
        "os": os,
        "sys": sys,
        "requests": requests,
        "settings": settings,
        "connection": connection,
        "last_query": last_query,
        "explain": lambda *a, **kw: sys.stdout.write(explain(*a, **kw)) and None,
    }
    models = __import__("strut.models", fromlist=["*"])
    for key, attr in vars(models).items():
        if isinstance(attr, type) and issubclass(attr, Model):
            context[key] = attr

    try:
        from IPython.terminal.embed import InteractiveShellEmbed

        sh = InteractiveShellEmbed.instance(banner1=banner)
    except ImportError:
        pass
    else:
        sh(local_ns=context)
        return
    from code import interact

    interact(banner, local=context)
