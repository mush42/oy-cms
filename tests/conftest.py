import pytest
import starlit
from flask import _request_ctx_stack
from flask_principal import Identity, identity_changed
from webtest import TestApp
from flask_security import login_user
from starlit.boot.exts.sqla import db as sqla_db
from starlit.boot.exts.admin import admin
from starlit.modules.editable_settings.models import SettingsProfile
from starlit.boot.exts.security import user_datastore


@pytest.fixture(scope="function")
def app():
    # Flask-Admin bug, see: https://stackoverflow.com/a/31712050
    admin._views = []

    app = starlit.create_app(config=dict(
        TESTING=True,
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SECURITY_PASSWORD_SALT = '540SDW4426HCAER56546aDrw213d2a6b9a94e15b5d'
    ))
    yield app


@pytest.fixture(scope="function")
def client(app):
    yield TestApp(app)

@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        sqla_db.create_all()
        yield sqla_db
        sqla_db.drop_all()


@pytest.fixture
def user(app, db):
    sp = SettingsProfile(name=u'Starlit', is_active=True)
    db.session.add(sp)
    user = user_datastore.create_user(
        user_name=u'admin',
        email=u'admin@localhost',
        password=u'admin')
    db.session.commit()
    def set_user():
        _request_ctx_stack.top.user = user
        identity_changed.send(app, identity=Identity(user.id))
    app.before_request(set_user)
    yield user
