import click

from .commands.init import init


@click.group()
def cli():
    pass


cli.add_command(init)
