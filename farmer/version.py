import click
import pkg_resources


def get_package_versions():
    distributions = [dist for dist in pkg_resources.working_set if dist.project_name.startswith(__package__)]
    return {dist.project_name: dist.version for dist in distributions}


def print_package_versions():
    for package, version in sorted(get_package_versions().items()):
        click.echo('{} {}'.format(package, version))
