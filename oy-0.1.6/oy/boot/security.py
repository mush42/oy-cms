from werkzeug.local import LocalProxy
from flask import current_app, request, url_for, session
from flask_security import Security, SQLAlchemyUserDatastore
from flask_wtf import CSRFProtect
from oy.boot.sqla import db
from oy.models.user import User, Role
from oy.babel import gettext, lazy_gettext
from .flask_security_forms.login import OyLoginForm
from .flask_security_forms.recover import OyRecoverPasswordForm


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()


def security_processer():
    if request.blueprint != "security":
        return
    if request.endpoint == "security.login":
        form = OyLoginForm()
        if form.validate_on_submit():
            session["lang"] = form.lang.data
    elif request.endpoint == "security.logout" and "lang" in session:
        session.pop("lang")


def initialize_security(app):
    security.init_app(
        app,
        login_form=OyLoginForm,
        forgot_password_form=OyRecoverPasswordForm,
        datastore=user_datastore,
    )
    app.before_request(security_processer)
    CSRFProtect(app)
