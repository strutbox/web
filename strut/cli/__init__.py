import os
from pkgutil import walk_packages

import click


def print_revision(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    try:
        click.echo(os.environ["BUILD_REVISION"])
    except KeyError:
        raise click.ClickException("Unknown BUILD_REVISION")
    ctx.exit()


@click.group()
@click.version_option()
@click.option(
    "--revision",
    expose_value=False,
    is_flag=True,
    is_eager=True,
    callback=print_revision,
    help="Show the git revision and exit.",
)
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
