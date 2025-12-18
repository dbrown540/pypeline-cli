import click

from .commands.init import init
from .commands.sync_deps import sync_deps


@click.group()
def cli():
    pass


cli.add_command(init)
cli.add_command(sync_deps)
