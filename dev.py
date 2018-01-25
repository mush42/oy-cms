import os 
from flask_security import login_user
from tempfile import mkdtemp
from starlit import create_app
from starlit.boot.exts.security import user_datastore
from starlit.boot.exts.sqla import db
from starlit.modules.core.models import User, Role, Site
from starlit.modules.page.models import Page

TEMP_DIR = mkdtemp()  
DB_FILE = os.path.join(TEMP_DIR, 'data.db')
UPLOADS_PATH = os.path.join(TEMP_DIR, "uploads")

if not os.path.exists(UPLOADS_PATH):
    os.mkdir(UPLOADS_PATH)

def create_defaults():
    site = Site(name=u'Starlit Test')
    db.session.add(site)
    su_role = Role(name='admin')
    db.session.add(su_role)
    su = user_datastore.create_user(
        user_name='admin',
        email='admin@localhost',
        password='admin',
        roles=[su_role]
    )
    db.session.commit()

config = dict(
    DEBUG=True,
    SQLALCHEMY_DATABASE_URI="sqlite:///%s" %DB_FILE,
    SECURITY_PASSWORD_SALT = '540SDW4426HCAER56546aDrw213d2a6b9a94e15b5d',
    UPLOADS_PATH=UPLOADS_PATH,
)

app = create_app(config=config)


@app.before_first_request
def do_this():
    login_user(User.query.one())
    db.session.add(Page(title='My Page', content='hey'))
    db.session.add(Page(title='Home', content='Home', slug='index'))
    db.session.commit()

if os.path.exists(DB_FILE):
    os.unlink(DB_FILE)
with app.app_context():
    db.create_all()
    create_defaults()
