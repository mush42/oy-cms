import os
import json
import click
from dateutil.parser import parse
from werkzeug import import_string
from flask.cli import FlaskGroup
from starlit.boot.exts.sqla import db
from starlit.boot.exts.security import user_datastore
from starlit.modules.core.models import User, Role


def create_users(objs):
    roles = Role.query.all()
    id_to_role = {role.id: role for role in roles}
    for obj in objs:
        user_roles = [id_to_role[i] for i in obj.pop('roles')]
        user_datastore.create_user(roles=user_roles, **obj)
    db.session.commit()


def deserialize_instances(model_name, objs, fixtures_root=""):
    if model_name.endswith(".User"):
        return create_users(objs)
    model = import_string(model_name)
    for obj in objs:
        for k, v in obj.items():
            if hasattr(v, 'strip') and v.startswith('_file'):
                to_read = os.path.join(fixtures_root, '_files', v.lstrip('_file:').strip())
                obj[k] = open(to_read, 'r').read()
            elif 'date' in k:
                    obj[k] = parse(v)
        instance = model(**obj)
        yield instance


def install_fixtures_factory(cwd):
    fixtures_root = os.path.join(cwd, 'fixtures')
    fixtures_json = os.path.join(fixtures_root, 'data.json')
    def install_fixtures():
        """Installs dummy pages and users."""
        fixtures_file = open(fixtures_json, 'r')
        click.echo('Installing fixtures in the database')
        for model_defn  in json.load(fixtures_file):
            for model_name, objs in model_defn.items():
                click.echo("Installing fixtures for: " + model_name)
                for instance in deserialize_instances(model_name, objs, fixtures_root=fixtures_root):
                    db.session.add(instance)
                    db.session.commit()
    return install_fixtures
