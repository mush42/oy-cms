import click
from flask import current_app
from flask.cli import with_appcontext
from flask_security.utils import hash_password
from oy.boot.sqla import db
from oy.helpers import is_valid_email
from oy.models.user import User, Role
from . import oy_group


def _prompt_for_user_details(user_name=None, email=None):
    from oy.boot.security import user_datastore

    if user_name is None:
        user_name = click.prompt(
            text="username (default admin)", default="admin", show_default=False
        )
        if user_datastore.find_user(user_name=user_name):
            click.secho(
                "Error: A user with the same username already exists.", fg="red"
            )
            return _prompt_for_user_details()
    if email is None:
        email = click.prompt(text="email address")
        if user_datastore.find_user(email=email):
            click.secho(
                "Error: A user with the same email already address exists.", fg="red"
            )
            return _prompt_for_user_details(user_name=user_name)
        elif not is_valid_email(email):
            click.secho("Invalid email address! Please try again.", fg="red")
            return _prompt_for_user_details(user_name=user_name)
    password = click.prompt(text="password", hide_input=True)
    if not len(password) >= 6:
        click.secho("Passwords should be at least 6 characters.", fg="red")
        return _prompt_for_user_details(user_name, email)
    password_confirm = click.prompt(text="confirm password", hide_input=True)
    if password != password_confirm:
        click.secho("Passwords do not match", fg="red")
        return _prompt_for_user_details(user_name, email)
    return user_name, email, password


@oy_group.command(name="createuser")
@click.option(
    "--noinput",
    "-n",
    help="Create a new user with a username of 'admin' and a password of 'adminpassword'",
    is_flag=True,
)
@click.option(
    "--superuser", "-su", help="Create a user with the role of *admin*.'", is_flag=True
)
@with_appcontext
def createuser(noinput, superuser):
    """Create a new super-user account"""
    from oy.boot.security import user_datastore

    usertype = "super" if superuser else ""
    click.echo(f"Creating a new {usertype} user account...")
    if not noinput:
        user_name, email, password = _prompt_for_user_details()
    else:
        user_name = "admin"
        email = "admin@local.host"
        password = "adminpass"
        if user_datastore.find_user(user_name=user_name):
            click.secho("User already exists.", fg="red")
            return
    if superuser:
        role = user_datastore.find_or_create_role("admin")
    else:
        role = user_datastore.find_or_create_role("staff")
    user_datastore.create_user(
        user_name=user_name, email=email, password=hash_password(password), roles=[role]
    )
    db.session.commit()
    click.echo()
    click.secho(f"{usertype} User created successfully.", fg="green", bold=True)
    click.secho("^" * 12, fg="red")
    click.secho(
        f"User account details: username={user_name}, password={password}",
        fg="red",
        bold=True,
    )
    if noinput:
        click.secho("Please change the default password.", fg="red", bold=True)
    click.secho("^" * 12, fg="red")
    click.echo("\r\n")
