from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_continuum import make_versioned


db = SQLAlchemy()
migrate = Migrate()
make_versioned(plugins=[FlaskPlugin()])

