import click


@click.command()
@click.option("--fake", is_flag=True)
@click.argument("migration_name", required=False)
def migrate(fake, migration_name):
    "Apply database migrations."
    import strut

    strut.setup()

    from django.core.management import call_command

    app_label = None
    if migration_name:
        app_label = "strut"

    call_command(
        "migrate", migration_name=migration_name, app_label=app_label, fake=fake
    )
