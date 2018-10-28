import click
from flask import current_app
from .database import database_group, create_db, drop_db, clean_db
from .user import createsuperuser
from .fixtures import install_fixtures


def starlit_group():
    """Perform tasks related to Starlit CMS"""


def create_all():
    """Automatically run essential commands"""
    click.echo()
    click.secho("~~~~~~~~~~~~~~~~~~~~~~~", fg="green")
    create_db()
    createsuperuser(noinput=True)
    install_fixtures()
    click.secho("~~~~~~~~~~~~~~~~~~~~~", fg="green", bold=True)


def register_cli_commands():
    """Add starlit command line interface"""
    starlit_cli = current_app.cli.group(name="starlit")(starlit_group)
    starlit_cli.command(name="createall")(create_all)
    starlit_cli.command(name="install-fixtures")(install_fixtures)
    starlit_cli.command(name="create-super-user")(createsuperuser)
    database_cli = starlit_cli.group(name="db")(database_group)
    database_cli.command(name="create")(create_db)
    database_cli.command(name="drop")(drop_db)
    database_cli.command(name="clean")(clean_db)
