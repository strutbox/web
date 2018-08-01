import click


@click.command()
@click.option("--generate", is_flag=True)
@click.argument("migration_name", required=False)
def migrate(generate, migration_name):
    "Apply database migrations."
    import strut

    strut.setup()

    from django.core.management import call_command

    if generate:
        call_command("makemigrations", "strut")

    call_command("migrate", app_label=None, migration_name=migration_name)
