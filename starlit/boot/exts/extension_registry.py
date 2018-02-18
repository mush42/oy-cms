from flask import current_app
from flask_wtf import CSRFProtect
from starlit.boot.exts.sqla import db, migrate
from starlit.boot.exts.babel import babel
from starlit.boot.exts.security import initialize_security


def initialize_core_exts():
    app = current_app._get_current_object()
    CSRFProtect(app)
    db.init_app(app)
    migrate.init_app(app, db=db)
    babel.init_app(app)
    initialize_security(app)
