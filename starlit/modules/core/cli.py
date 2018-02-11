import re
import os
import json
import click
from flask import current_app
from dateutil.parser import parse
from werkzeug import import_string
from flask.cli import FlaskGroup
from starlit.boot.exts.sqla import db
from starlit.modules.core.models import User, Role


_email_re = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", flags=re.IGNORECASE)

user_not_created_msg = """
Super-user required!

Please create at least one super user before attempting to install fixdtures.
    At anytime, you can use the `create-super-user` command to create a new super-user.
"""



def createsuperuser(user_name=None, email=None):
    """Create a super-user account"""
    from starlit.boot.exts.security import user_datastore
    if user_name is None:
        user_name = click.prompt(
            text="username (default 'admin')",
            default="admin",
            show_default=False,
        )
        if user_datastore.find_user(user_name=user_name):
            click.echo("Error: A user with the same username already exists.")
            return createsuperuser()
    if email is None:
        email = click.prompt(text="email address:")
        if user_datastore.find_user(email=email):
            click.echo("Error: A user with the same email already exists.")
            return createsuperuser(user_name=user_name)
        elif _email_re.match(email) is None:
            click.echo("Invalid email address! Please try again.")
            return createsuperuser(user_name=user_name)
    password = click.prompt(
        text="password:",
        hide_input=True,
    )
    if not len(password) >= 6:
        click.echo("Passwords should be at least 6 characters.")
        return createsuperuser(user_name, email)
    password_confirm = click.prompt(
        text="confirm password:",
        hide_input=True,
    )
    if password != password_confirm:
        click.echo("Passwords do not match")
        return createsuperuser(user_name, email)
    admin_role = user_datastore.find_or_create_role('admin')
    user_datastore.create_user(
        user_name=user_name,
        email=email,
        password=password,
        roles=[admin_role]
    )
    db.session.commit()
    click.echo("User created successfully.")


def deserialize_instances(model_name, objs, root_path):
    model = import_string(model_name)
    for obj in objs:
        for k, v in obj.items():
            if hasattr(v, 'strip') and v.startswith('_file'):
                to_read = os.path.join(root_path, 'fixtures', '_files', v.lstrip('_file:').strip())
                obj[k] = open(to_read, 'r').read()
            elif 'date' in k:
                    obj[k] = parse(v)
        instance = model(**obj)
        yield instance


def _aggregated_fixture():
    """Iterates over app modules to find fixtures and extracts them"""
    for module in current_app.modules.values():
        try:
            with module.open_resource('fixtures/data.json') as datafile:
                yield json.load(datafile), module.root_path
        except IOError:
            continue
        except JSONDecodeError:
            click.echo("Error loading fixtures for module: " + module.import_name)
            continue


def install_fixtures():
    """Installs dummy content to kick start your starlit powered site."""
    if not User.query.filter(User.active==True).count():
        click.echo(user_not_created_msg)
        if click.prompt("Would you like to create one now? (y/n):", default="y") == 'y':
            createsuperuser()
        else:
            raise click.Abort()
    click.echo('Installing fixtures in the database')
    for model_defn, root_path in _aggregated_fixture():
        for model_import_path, objs in model_defn.items():
            click.echo("Installing fixtures for: " + model_import_path)
            for instance in deserialize_instances(model_import_path, objs, root_path):
                db.session.add(instance)
                db.session.commit()
    click.echo()
    click.echo("===============")
    click.echo("Finished installing all available fixtures.")
    