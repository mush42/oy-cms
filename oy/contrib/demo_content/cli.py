import os
import sys
import click
import json
from dateutil.parser import parse
from sqlalchemy.exc import IntegrityError
from werkzeug import import_string
from werkzeug.utils import cached_property
from flask import current_app
from flask.cli import with_appcontext
from oy.exceptions import OyException
from oy.boot.sqla import db
from oy.models.user import User
from oy.cli.database import create_db
from oy.cli.user import createuser


user_not_created_msg = """
Super-user required!

Please create at least one super user before attempting to install fixdtures.
    At anytime, you can use the `createuser` command to create a new super-user.
"""


class BadlyFormattedFixture(OyException):
    """Raised when a fixture could not be decoded"""


class FixtureInstaller(object):
    """A utility class to install fixtures from modules."""

    def __init__(self, module):
        self.module = module

    def deserialize_instance(self, model, **obj):
        """Given a model and fields as a dict of keyword args
        this will return an instance of model with the fields
        """
        for k, v in obj.items():
            if hasattr(v, "strip") and v.startswith("__files__"):
                to_read = os.path.join(
                    self.module.root_path, "fixtures", "__files__", v[10:]
                )
                obj[k] = open(to_read, "r").read()
            elif "date" in k:
                obj[k] = parse(v)
        return model(**obj)

    @cached_property
    def fixtures(self):
        """Returns the json decoded fixture or None"""
        try:
            with self.module.open_resource("fixtures/data.json") as datafile:
                return json.load(datafile)
        except IOError:
            return
        except json.JSONDecodeError:
            raise BadlyFormattedFixture(
                f"Error deserializing fixtures for:  {self.module.name}."
            )

    def install(self):
        if not self.fixtures:
            return
        for model_import_path, objs in self.fixtures.items():
            model = import_string(model_import_path)
            for obj in objs:
                instance = self.deserialize_instance(model, **obj)
                errors = []
                try:
                    db.session.add(instance)
                    db.session.commit()
                except IntegrityError as err:
                    db.session.rollback()
                    errors.append(err)
                    continue
                for e in errors:
                    click.secho(repr(e), fg="red")


@click.command("install-fixtures")
@with_appcontext
def install_fixtures():
    """Install dummy content."""
    if not User.query.filter(User.active == True).count():
        click.secho(user_not_created_msg, fg="yellow")
        if click.prompt("Would you like to create one now? (y/n):", default="y") == "y":
            createsuperuser(noinput=False)
        else:
            raise click.Abort()
    click.echo("Installing fixtures in the database")
    click.echo("~~~~~~~~~~~~~~~~~")
    click.echo()
    for module in current_app.modules.values():
        fixtured = FixtureInstaller(module)
        if not fixtured.fixtures:
            continue
        click.secho("Installing fixtures for module: " + module.import_name, fg="blue")
        fixtured.install()
    click.echo()
    click.secho("===============", fg="green")
    click.secho("Finished installing all available fixtures.", fg="green", bold=True)


@click.command(name="createall")
@click.pass_context
@with_appcontext
def create_all(ctx):
    """Automatically Install all demo data."""
    click.echo()
    click.secho("~" * 50, fg="green")
    ctx.invoke(create_db)
    ctx.invoke(createuser, noinput=True, superuser=True)
    click.echo("^" * 14)
    click.echo("Superuser account details: (username=admin) (password=adminpass)")
    click.echo("Please change the default password.")
    click.echo("^" * 14)
    ctx.invoke(install_fixtures)
    click.secho("~" * 50, fg="green", bold=True)
