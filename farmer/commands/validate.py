import logging
import os
import warnings

import click
from pykwalify.core import Core
from pykwalify import errors
import ruamel

from farmer import output
from farmer.api import (
    VMFarmsAPIClient,
    VMFarmsAPIError,
)
from farmer.config import load_config


warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)


@click.command()
@click.argument('config')
def cli(config):
    """
    Validate vmfarms.yml for common syntax/option errors.
    """
    # Like all good third-party apps, pykwalify messes up its "magic" logging config
    logger = logging.getLogger('pykwalify.core')
    logger.addHandler(logging.NullHandler())

    schema = os.path.join(os.path.dirname(__file__), 'validate_schema.yml')
    try:
        core = Core(source_file=config, schema_files=[schema])
    except errors.CoreError as exc:
        if 'Unable to load any data from source yaml file' in exc.msg:
            raise click.ClickException('Config file appears to be invalid YAML')
        if 'Provided source_file do not exists on disk' in exc.msg:
            raise click.ClickException('Config file not found: ' + config)

    core.validate(raise_exception=False)
    for error in core.errors:
        click.echo(error)
        if 'does not match any regex' in error.msg and error.path == '':
            click.echo('- Hint: "{0}" is not a valid hook'.format(error.key))
        elif 'was not defined' in error.msg:
            click.echo('- Hint: "{0}" is not a valid option for {1} hook'.format(error.key, error.path.split('/')[1]))
        elif 'not a list' in error.msg and len(error.path.split('/')) == 2:
            click.echo('- Hint: {0} hook is malformed (did you forget the dash?)'.format(error.path.split('/')[1]))
        elif 'not a list' in error.msg and error.path.split('/')[-1] == 'roles':
            click.echo("- Hint: roles must be a list: eg. ['{0}']".format(error.value))
        click.echo('\n')
