import click

from farmer import output
from farmer.api import (
    VMFarmsAPIClient,
    VMFarmsAPIError,
)
from farmer.config import load_config


@click.command()
def cli():
    """
    List your applications and environments.
    """
    config = load_config()
    try:
        client = VMFarmsAPIClient.from_config(config)
        applications = client.get('applications')['results']
        if not applications:
            click.echo(output.yellow("Didn't find any registered applications!"))
            return

        click.echo('Your registered application(s) and their available environment(s):')
        for app in applications:
            app['env_names'] = ', '.join(app['environments']) or 'n/a'
            click.echo('\n{app[name]}: \n\tenvironments: {app[env_names]}'.format(app=app))
    except VMFarmsAPIError as error:
        output.die(error.message, error.description)
