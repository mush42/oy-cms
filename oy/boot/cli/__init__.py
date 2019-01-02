import click
from flask import current_app
from .database import database_group, create_db, drop_db, clean_db
from .user import createsuperuser
from .fixtures import install_fixtures


def bound_oy_group():
    """Perform tasks related to Oy CMS.
    It is being used when an application
    context is available.
    """


def create_all():
    """Automatically run essential commands"""
    click.echo()
    click.secho("~" * 50, fg="green")
    create_db()
    createsuperuser(noinput=True)
    install_fixtures()
    click.secho("~" * 50, fg="green", bold=True)


def register_cli_commands():
    """Add oy command line interface"""
    group_factory = current_app.cli.group(name="oy")
    oy_cli = group_factory(bound_oy_group)
    oy_cli.command(name="createall")(create_all)
    oy_cli.command(name="install-fixtures")(install_fixtures)
    oy_cli.command(name="create-super-user")(createsuperuser)
    database_cli = oy_cli.group(name="db")(database_group)
    database_cli.command(name="create")(create_db)
    database_cli.command(name="drop")(drop_db)
    database_cli.command(name="clean")(clean_db)
