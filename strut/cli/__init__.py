import click
from pkgutil import walk_packages


@click.group()
def main():
    """\b
   _____________  __  ________
  / __/_  __/ _ \/ / / /_  __/
 _\ \  / / / , _/ /_/ / / /
/___/ /_/ /_/|_|\____/ /_/
"""
    pass


for loader, module_name, is_pkg in walk_packages(__path__, __name__ + '.'):
    # this causes a Runtime error with model conflicts
    # module = loader.find_module(module_name).load_module(module_name)
    module = __import__(module_name, globals(), locals(), ['__name__'])
    for v in vars(module).values():
        if isinstance(v, click.Command):
            main.add_command(v)
