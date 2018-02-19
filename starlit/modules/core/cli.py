import re
import click
from flask import current_app
from flask.cli import FlaskGroup
from starlit.boot.exts.sqla import db
from starlit.modules.core.models import User, Role


_email_re = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    flags=re.IGNORECASE
  )

user_not_created_msg = """
Super-user required!

Please create at least one super user before attempting to install fixdtures.
    At anytime, you can use the `create-super-user` command to create a new super-user.
"""


def _prompt_for_user_details(user_name=None, email=None):
    from starlit.boot.exts.security import user_datastore
    if user_name is None:
        user_name = click.prompt(
            text="username (default admin)",
            default="admin",
            show_default=False,
        )
        if user_datastore.find_user(user_name=user_name):
            click.echo("Error: A user with the same username already exists.")
            return _prompt_for_user_details()
    if email is None:
        email = click.prompt(text="email address")
        if user_datastore.find_user(email=email):
            click.echo("Error: A user with the same email already address exists.")
            return _prompt_for_user_details(user_name=user_name)
        elif _email_re.match(email) is None:
            click.echo("Invalid email address! Please try again.")
            return _prompt_for_user_details(user_name=user_name)
    password = click.prompt(
        text="password",
        hide_input=True,
    )
    if not len(password) >= 6:
        click.echo("Passwords should be at least 6 characters.")
        return _prompt_for_user_details(user_name, email)
    password_confirm = click.prompt(
        text="confirm password",
        hide_input=True,
    )
    if password != password_confirm:
        click.echo("Passwords do not match")
        return _prompt_for_user_details(user_name, email)
    return user_name, email, password


@click.option(
    '--noinput', '-n',
    help="Create a new user with a username of 'admin' and a password of 'adminpassword'",
    is_flag=True)
def createsuperuser(noinput):
    """Create a new super-user account"""
    from starlit.boot.exts.security import user_datastore
    if not noinput:
        user_name, email, password = _prompt_for_user_details()
    else:
        user_name = 'admin'
        email = 'admin@local.host'
        password = 'adminpass'
        if user_datastore.find_user(user_name=user_name):
            click.echo("User already exists.")
            return
    admin_role = user_datastore.find_or_create_role('admin')
    user_datastore.create_user(
        user_name=user_name,
        email=email,
        password=password,
        roles=[admin_role]
    )
    db.session.commit()
    click.echo()
    click.echo("User created successfully.")


def install_fixtures():
    """Installs dummy content to kick start your starlit powered site."""
    if not User.query.filter(User.active==True).count():
        click.echo(user_not_created_msg)
        if click.prompt("Would you like to create one now? (y/n):", default="y") == 'y':
            createsuperuser(noinput=False)
        else:
            raise click.Abort()
    click.echo('Installing fixtures in the database')
    click.echo('~~~~~~~~~~~~~~~~~')
    click.echo()
    for module in current_app.modules.values():
        if not module.fixtures:
            continue
        click.echo("Installing fixtures for module: " + module.import_name)
        module.install_fixtures()
    click.echo()
    click.echo("===============")
    click.echo("Finished installing all available fixtures.")
    