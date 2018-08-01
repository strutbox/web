import click
from pkgutil import walk_packages


@click.group()
@click.version_option()
def main():
    """\b
   _____________  __  ________
  / __/_  __/ _ \/ / / /_  __/
 _\ \  / / / , _/ /_/ / / /
/___/ /_/ /_/|_|\____/ /_/
"""


for loader, module_name, is_pkg in walk_packages(__path__, __name__ + "."):
    module = __import__(module_name, globals(), locals(), ["__name__"])
    cmd = getattr(module, module_name.rsplit(".", 1)[-1])
    if isinstance(cmd, click.Command):
        main.add_command(cmd)
