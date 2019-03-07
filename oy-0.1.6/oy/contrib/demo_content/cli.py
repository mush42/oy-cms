import click
from flask import current_app
from flask.cli import with_appcontext
from oy.models.user import User
from oy.cli.database import create_db
from oy.cli.user import createuser
from .utils import FixtureInstaller


user_not_created_msg = """
Super-user required!

Please create at least one super user before attempting to install fixdtures.
    At anytime, you can use the `createuser` command to create a new super-user.
"""


@click.command("install-fixtures")
@click.argument("module", default=None, required=False)
@click.pass_context
@with_appcontext
def install_fixtures(ctx, module):
    """Add some dummy content to the database."""
    if not User.query.filter(User.active == True).count():
        click.secho(user_not_created_msg, fg="yellow")
        if click.prompt("Would you like to create one now? (y/n):", default="y") == "y":
            ctx.invoke(createsuperuser, noinput=False, superuser=True)
        else:
            raise click.Abort()
    click.echo("Adding some demo data to the database")
    click.echo("~" * 12)
    click.echo()
    module = module or current_app.modules.keys()
    for m in module:
        if not current_app.modules.get(m):
            click.secho(
                f"The module {m} was not found among the app registered modules.",
                fg="red",
            )
            raise click.Abort()
    for mod in (current_app.modules[k] for k in module):
        fixtured = FixtureInstaller(mod)
        if not fixtured.fixtures:
            continue
        click.secho(f"Adding demo data from module: {mod.import_name}", fg="yellow")
        fixtured.install()
    click.echo()
    click.secho("=" * 12, fg="green")
    click.secho("Finished adding all available demo data.", fg="green", bold=True)


@click.command(name="createall")
@click.pass_context
@with_appcontext
def create_all(ctx):
    """Automatically Install all demo data."""
    click.echo()
    click.secho("~" * 12, fg="green")
    ctx.invoke(create_db)
    ctx.invoke(createuser, noinput=True, superuser=True)
    click.echo()
    ctx.invoke(install_fixtures)
    click.secho("~" * 12, fg="green", bold=True)
