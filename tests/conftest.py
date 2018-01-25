import pytest
import starlit
from webtest import TestApp
from flask_security import login_user
from starlit.boot.exts.sqla import db as sqla_db
from starlit.modules.core.models import Site
from starlit.boot.exts.security import user_datastore

@pytest.fixture(scope="function")
def app():
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
    site = Site(name=u'Starlit')
    db.session.add(site)
    usr = user_datastore.create_user(
        user_name=u'admin',
        email=u'admin@localhost',
        password=u'admin')
    db.session.commit()
    app.before_request(lambda: login_user(usr))
