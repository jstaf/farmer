"""
This module provides the main entry point.
"""

import click
import stevedore

from farmer.version import print_package_versions


class FarmerAliasedGroup(click.Group):
    """
    AliasedGroup supports command abbreviations.
    """
    def get_command(self, ctx, command_name):
        # Search builtin commands (normal behaviour).
        command = click.Group.get_command(self, ctx, command_name)
        if command is not None:
            return command

        # Match against explicit aliases.
        if command_name in ctx.obj.get('aliases'):
            actual_command = ctx.obj['aliases'][command_name]
            return click.Group.get_command(self, ctx, actual_command)

        # Match commands by automatic abbreviation of the command name (e.g.,
        # 'st' will match 'status')
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(command_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


class FarmerCLI(click.Group):
    """
    The main Farmer entry point.
    """
    def __init__(self, callback=None, **attrs):
        # Pass the context object to the callback function.
        callback.__click_pass_context__ = True
        self.context_settings = {
            'help_option_names': ('-h', '--help'),
        }
        super(FarmerCLI, self).__init__(
            callback=callback,
            context_settings=self.context_settings,
            **attrs
        )

    def list_commands(self, ctx):
        """
        List available commands.

        Args:
            ctx (object): The ``click`` context object. This is populated
                automatically when using the decorator syntax.

        Returns:
            List of available commands.
        """
        return sorted(stevedore.ExtensionManager('farmer.commands', on_load_failure_callback=self._on_load_failure_callback).names())

    def get_command(self, ctx, name):
        """
        Load the given command.

        Args:
            ctx (object): The ``click`` context object. This is populated
                automatically when using the decorator syntax.
            name (str): Name of the command.

        Returns:
            The command's ``cli()`` entry point.
        """
        try:
            return stevedore.DriverManager('farmer.commands', name).driver
        # Let click handle missing commands internally.
        except RuntimeError:
            pass

    @staticmethod
    def _on_load_failure_callback(manager, entrypoint, exception):
        click.echo("Error: Cannot load '{entrypoint.name}' ({entrypoint.module_name}). Exception:".format(entrypoint=entrypoint), err=True)
        click.echo('\n    {exception.__class__.__name__}: {exception.message}\n'.format(exception=exception), err=True)


def aliases(aliases, **attrs):
    if not isinstance(aliases, dict):
        raise TypeError('aliases must be a dictionary')

    def decorator(command):
        command.context_settings = {'obj': {'aliases': aliases}}
        return command
    return decorator


def show_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    print_package_versions()
    ctx.exit()


@click.group(cls=FarmerCLI)
@click.option(
    '--version',
    callback=show_version,
    expose_value=False,
    help='Show the version and exit.',
    is_eager=True,
    is_flag=True,
)
@click.pass_context
# Common kwargs (e.g., debug) are passed in by FarmerCLI.
def cli(ctx, **kwargs):
    ctx.obj = kwargs
    if ctx.invoked_subcommand != 'config':
        try:
            from farmer import config
            config.load_config()
        except TypeError:
            raise click.ClickException('Oops! Cannot find Farmer configuration. Run `farmer config` first.')
