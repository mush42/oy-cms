import pytest
import starlit
from flask import _request_ctx_stack
from flask_principal import Identity, identity_changed
from webtest import TestApp
from flask_security import login_user
from starlit.boot.exts.sqla import db as sqla_db
from starlit.modules.core.models import Role
from starlit.modules.editable_settings.models import SettingsProfile
from starlit.boot.exts.security import user_datastore


@pytest.fixture(scope="function")
def app():
    app = starlit.create_app(__name__, config=dict(
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
        sp = SettingsProfile(name=u'Starlit', is_active=True)
        sqla_db.session.add(sp)
        sqla_db.session.commit()
        yield sqla_db
        sqla_db.drop_all()


@pytest.fixture
def user_factory(app, db):
    def wrapped_user_factory(name="test_user", email='test@localhost', roles=None):
        if not roles:
            roles = ["admin"]        
        user = user_datastore.create_user(
            user_name=name,
            email=email,
            password=u'admin',
        )
        for role in roles:
            user.roles.append(user_datastore.find_or_create_role(name=role))
        db.session.commit()
        app.test_user = user
        def set_user():
            _request_ctx_stack.top.user = user
            identity_changed.send(app, identity=Identity(user.id))
        app.before_request(set_user)
        return user
    return wrapped_user_factory
