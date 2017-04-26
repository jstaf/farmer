import click
import pkg_resources


@click.command()
def cli():
    """
    Print the version and exit.
    """
    distributions = [dist for dist in pkg_resources.working_set if dist.project_name.startswith('farmer')]
    for distribution in sorted(distributions):
        click.echo('{} {}'.format(distribution.project_name, distribution.version))
