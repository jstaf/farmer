import click

from ..version import print_package_versions


@click.command()
def cli():
    """
    Show the version and exit.
    """
    print_package_versions()
