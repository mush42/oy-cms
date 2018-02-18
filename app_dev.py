import os 
import tempfile
import click
from starlit import create_app
from starlit.boot.exts.sqla import db
from starlit.contrib.admin import AdminPlugin


TEMP_DIR = tempfile.mkdtemp()  
UPLOADS_PATH = os.path.join(TEMP_DIR, "uploads")

if not os.path.exists(UPLOADS_PATH):
    os.mkdir(UPLOADS_PATH)

config = dict(
    DEBUG=True,
    SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite",
    #EXPLAIN_TEMPLATE_LOADING=True,
    SECURITY_PASSWORD_SALT = '540SDW4426HCAER56546aDrw213d2a6b9a94e15b5d',
    UPLOADS_PATH=UPLOADS_PATH,
)

app = create_app('dev', config=config)
app.use(AdminPlugin)


@app.cli.group(name="database")
def database():
    """Perform database operations"""


@database.command(name='create')
def create_db():
    """Create database tables."""
    with app.app_context():
        db.create_all()
    click.echo("Database tables created.")


@database.command(name='drop')
@click.option('--noinput', '-n', is_flag=True)
def drop_db(noinput):
    """Drop database tables"""
    click.echo("!!!!!!!!!")
    if not noinput:
        response = click.confirm("""This is a distructive operation. You will loose all  you data.\r\nDo you want to drop all database tables?""")
        if not response:
            raise click.Abort()
    with app.app_context():
        db.drop_all()
    click.echo("Database tables dropped")
