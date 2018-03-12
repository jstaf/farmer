import click
import dateparser
import requests
import sh

from farmer.config import load_config
from farmer.logdna import LogDNAClient


def parse_datetime(ctx, param, value):
    parsed_datetime = dateparser.parse(value)
    if not parsed_datetime:
        raise click.ClickException('Could not parse `{}` as datetime: {}'.format('/'.join(param.opts), value))
    return parsed_datetime


def prompt_logdna_service_key():
    """
    Prompt the user to create a service key.
    """
    # `config` and `export` both call this code. It is easier to test it as an
    # isolated function.
    config = load_config()
    click.echo('Farmer will prompt you to enter your LogDNA service key.')
    click.echo('If you have not created a service key yet, go to:\n\n    <https://app.logdna.com/manage/profile>\n')
    logdna_service_key = click.prompt('Enter your LogDNA service key')
    if config.get(config, 'logdna_service_key'):
        click.confirm('You have already configured Farmer with a LogDNA service key. Overwrite it?', abort=True)
    return logdna_service_key


@click.group()
@click.pass_context
def cli(ctx):
    """
    Export log lines from LogDNA.
    """


@cli.command()
@click.pass_context
def config(ctx):
    """
    Configure Farmer with your LogDNA key.

    To create a service key, go to:

        <https://app.logdna.com/manage/profile>
    """
    logdna_service_key = prompt_logdna_service_key()
    sh.farmer.config.set('logdna_service_key', logdna_service_key)


@cli.command()
@click.option(
    '-f', '--from', 'from_datetime',
    callback=parse_datetime,
    default='1 day ago',
    help='Start time for logs to export. Supports human readable dates.',
    metavar='DATETIME',
    show_default=True,
)
@click.option(
    '-t', '--to', 'to_datetime',
    callback=parse_datetime,
    default='now',
    help='End time for logs to export. Supports human readable dates.',
    metavar='DATETIME',
    show_default=True,
)
@click.option(
    '-n', '--num', 'size',
    help='Number of results to return.',
    type=int,
)
@click.option(
    '-h', '--host', 'hosts',
    help='Host to filter by. You may specify this multiple times.',
    multiple=True,
)
@click.option(
    '-a', '--app', 'apps',
    help='Application to filter by. You may specify this multiple times.',
    multiple=True,
)
@click.option(
    '-l', '--level', 'levels',
    help='Log level to filter by. You may specify this multiple times.',
    multiple=True,
)
@click.option(
    '-q', '--query',
    help='Limit results by search query. See <https://docs.logdna.com/docs/search>.',
)
@click.option(
    '--head', 'prefer', flag_value='head',
    help='Show first -n/--num lines of results.',
)
@click.option(
    '--tail', 'prefer', flag_value='tail',
    default=True,
    help='Show last -n/--num lines of results (default).',
)
@click.pass_context
def export(ctx, from_datetime, to_datetime, size, hosts, apps, levels, query, prefer):
    """
    Export log lines from LogDNA.

    LogDNA exports lines in JSON Lines format:

        <http://jsonlines.org/>

    For API details, refer to the LogDNA documentation:

        <https://docs.logdna.com/docs/v1-export-api>
    """
    # Attempt to load key from configuration.
    user_config = load_config()
    logdna_service_key = user_config.get(user_config, 'logdna_service_key')
    if not logdna_service_key:
        logdna_service_key = prompt_logdna_service_key()
        sh.farmer.config.set('logdna_service_key', logdna_service_key)

    logdna = LogDNAClient(logdna_service_key)
    try:
        lines = logdna.export(
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            size=size,
            hosts=','.join(hosts) if hosts else None,
            apps=','.join(apps) if apps else None,
            levels=','.join(levels) if levels else None,
            query=query,
            prefer=prefer
        )
    except requests.RequestException as exc:
        msg = 'There was a problem requesting logs from LogDNA. Exception:\n{}'.format(exc)
        raise click.ClickException(msg)

    for line in lines:
        click.echo(line)
