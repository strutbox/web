import click


@click.command()
@click.argument('migration_name', required=False)
def migrate(migration_name):
    'Apply database migrations.'
    # We need to explicitly setup Django first, otherwise migrate
    # will complain about not having any apps loaded yet.
    import django
    django.setup()

    from django.core.management import call_command
    call_command(
        'migrate',
        app_label=None,
        migration_name=migration_name,
    )
