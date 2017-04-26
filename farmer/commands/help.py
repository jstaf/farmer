import click


def get_help_recursive(group, ctx, commands):
    """
    Returns help for arbitrarily nested subcommands of the given click.Group.
    """
    try:
        command_name = commands.pop(0)
        group = group.get_command(ctx, command_name)
        if not group:
            raise click.ClickException('Invalid command: {}'.format(command_name))
    except IndexError:
        # end of subcommand chain
        return group.get_help(ctx)
    except AttributeError:
        # group is actually a command with no children
        return group.get_help(ctx)
    return get_help_recursive(group, ctx, commands)


@click.command()
@click.argument('command', nargs=-1)
@click.pass_context
def cli(ctx, command):
    """
    Show help for a command or subcommand.
    """
    farmer = ctx.parent.command
    commands = list(command)
    click.echo(get_help_recursive(farmer, ctx.parent, commands))
