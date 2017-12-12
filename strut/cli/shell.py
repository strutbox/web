import click


@click.command()
def shell():
    'Start interactive python shell.'

    banner = '''\
   _____________  __  ________
  / __/_  __/ _ \/ / / /_  __/
 _\ \  / / / , _/ /_/ / / /
/___/ /_/ /_/|_|\____/ /_/
'''
    from django.conf import settings
    context = {
        'settings': settings,
    }
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
