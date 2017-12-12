import click


@click.command()
@click.option('--generate', is_flag=True)
@click.argument('migration_name', required=False)
def migrate(generate, migration_name):
    'Apply database migrations.'
    # We need to explicitly setup Django first, otherwise migrate
    # will complain about not having any apps loaded yet.
    import django
    django.setup()

    from django.core.management import call_command

    if generate:
        call_command('makemigrations', args=['strut'])

    call_command(
        'migrate',
        app_label=None,
        migration_name=migration_name,
    )
