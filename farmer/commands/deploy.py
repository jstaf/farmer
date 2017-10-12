import click

from farmer import output
from farmer.api import (
    VMFarmsAPIClient,
    VMFarmsAPIError,
)
from farmer.config import load_config


@click.command()
@click.argument('app')
@click.argument('environment')
@click.option('-b', '--branch', help="Name of the branch that should be deployed.")
@click.option(
    '--open/--no-open', 'open_deploy',
    help='Open deploy page in portal automatically.',
    default=True, show_default=True
)
def cli(app, environment, branch, open_deploy):
    """
    Deploy an application to an environment.
    """
    config = load_config()
    try:
        client = VMFarmsAPIClient.from_config(config)
        application_list = client.get('applications')['results']
        selected_application = next(application for application in application_list if application['name'] == app)
        assert environment in selected_application['environments'], 'Invalid environment specified.'

        data = {
            'environment': environment,
            'branch': branch,
        }
        response = client.post('applications/{application_id}/builds'.format(**selected_application), data=data)
        build_id = response['id']
        deploy_url = client.url_for('builds', 'deploys', build_id)
    except AssertionError as exc:
        output.die(str(exc))
    except StopIteration:
        output.die('Invalid app specified.')
    except VMFarmsAPIError as error:
        output.die(error.message, error.description)
    else:
        output.success('Triggered deploy! Monitor it at <{}>.'.format(deploy_url))
        if open_deploy:
            click.launch(deploy_url)
