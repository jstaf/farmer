from functools import partial
import textwrap
import sys

import click


red = partial(click.style, fg='red')
green = partial(click.style, fg='green')
yellow = partial(click.style, fg='yellow')


def die(message, description=None):
    """
    Output an error message and exit.
    """
    click.echo(red('Error: {}'.format(message)), err=True)
    if description:
        click.echo('\n'.join(textwrap.wrap(description)), err=True)
    sys.exit(1)


def success(message):
    """
    Output a success message.
    """
    click.echo(green(message))
