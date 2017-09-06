# -*- coding: utf-8 -*-

import collections
import errno
import operator
import os

import click
import ruamel.yaml
import six

from farmer.config import (
    DEFAULT_CONFIG_DIR,
    load_config,
)


SCALARS = (six.binary_type,) + six.integer_types + six.string_types + (six.text_type,)


def dump_yaml(layered_config):
    return ruamel.yaml.round_trip_dump(layered_config.dump(layered_config),
                                       default_flow_style=False)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def yaml_unicode_representer(self, data):
    return self.represent_str(data.encode('utf-8'))


ruamel.yaml.representer.Representer.add_representer(six.text_type, yaml_unicode_representer)


def initialize_config():
    click.echo("Hi! It looks like you haven't configured Farmer yet.\n")
    token = click.prompt('Enter your VM Farms API token')
    mkdir_p(DEFAULT_CONFIG_DIR)
    config_filename = os.path.join(DEFAULT_CONFIG_DIR, 'farmer.yml')
    with open(config_filename, 'w') as config_file:
        config_file.write(ruamel.yaml.safe_dump({'token': token},
                                                default_flow_style=False,
                                                allow_unicode=True))


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    Manage Farmer configuration.
    """
    try:
        config = load_config()
    except TypeError:
        initialize_config()
    finally:
        config = load_config()

    if not config.get(config, 'token'):
        initialize_config()

    ctx.obj = {'config': load_config()}


@cli.command()
@click.argument('keyword')
@click.pass_context
def get(ctx, keyword):
    """
    Print a configuration setting.

    \b
    Example:

        farmer config get api_url
    """
    config = ctx.obj['config']
    try:
        value = operator.attrgetter(keyword)(config)
    except AttributeError as exc:
        raise click.ClickException(exc.message)
    if isinstance(value, SCALARS):
        click.echo(value)
    else:
        # Resolve top-most LayeredConfig config and dump it as YAML.
        click.echo(dump_yaml(value))


@cli.command('set')
@click.argument('keyword')
@click.argument('value')
@click.pass_context
def _set(ctx, keyword, value):
    """
    Set a configuration setting.

    \b
    Example:

        farmer config set vmfarms_api.token 97d3b36ff3914c4f44f836e339881d4e4b94eb7f
    """
    config = ctx.obj['config']
    tree = config
    keys = keyword.split('.')
    # Create a nested dictionary of preceding keys.
    for idx, key in enumerate(keys[:-1]):
        if hasattr(tree, key):
            if isinstance(getattr(tree, key), SCALARS):
                raise click.ClickException('{} exists and is not a map.'.format('.'.join(keys[:idx + 1])))
        else:
            setattr(tree, key, {})
        tree = getattr(tree, key)
    if isinstance(tree, collections.MutableMapping):
        tree[keys[-1]] = value
    else:
        tree.set(tree, keys[-1], value, 'roundtripyamlfile')
    config.write(config)
    config._sources[1].save()


@cli.command()
@click.pass_context
def edit(ctx):
    """
    Edit your Farmer configuration file.
    """
    config = ctx.obj['config']
    click.edit(filename=config._sources[1].yaml_filename)


@cli.command()
@click.pass_context
def dump(ctx):
    """
    Dump loaded configuration.
    """
    config = ctx.obj['config']
    click.echo(dump_yaml(config))
