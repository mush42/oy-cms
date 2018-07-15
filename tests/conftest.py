import pytest
import starlit
from webtest import TestApp
from starlit.boot.sqla import db as sqla_db
from starlit.boot.security import user_datastore


@pytest.fixture(scope="module")
def app():
    app = starlit.create_app(__name__, config=dict(
        SECRET_KEY='testing-secret-key',
        TESTING=True,
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SECURITY_PASSWORD_HASH='plaintext',
    ))
    yield app


@pytest.fixture(scope="module")
def client(app):
    yield TestApp(app)

def create_user():
    admin_role = user_datastore.find_or_create_role('admin')
    return user_datastore.create_user(
        user_name='admin',
        email='admin@localhost.com',
        password='mmmaaa',
        roles=[admin_role]
    )


@pytest.fixture(scope="module")
def db(request, app):
    with app.app_context():
        sqla_db.create_all()
        user = create_user()
        sqla_db.session.commit()
        app.test_user = user
        if getattr(request.module, '__install_fixtures__', True):
            for mod in app.modules.values():
                mod.install_fixtures()
        yield sqla_db
        sqla_db.drop_all()

