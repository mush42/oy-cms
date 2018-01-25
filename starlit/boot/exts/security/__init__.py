from werkzeug.local import LocalProxy
from flask import current_app, request, url_for, session
from flask_security import Security, SQLAlchemyUserDatastore
from flask_admin import helpers as admin_helpers
from starlit.boot.exts.sqla import db
from starlit.boot.exts.admin import admin
from starlit.modules.core.models import User, Role
from starlit.babel import gettext, lazy_gettext
from .forms.login import StarlitLoginForm
from .forms.recover import StarlitRecoverPasswordForm


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()


def security_processer():
    if request.blueprint != 'security':
        return
    if request.endpoint == 'security.login':
        form = StarlitLoginForm()
        if form.validate_on_submit():
            session['lang'] = form.lang.data
    elif request.endpoint == 'security.logout' and 'lang' in session:
        session.pop('lang')


def initialize_security(app):
    security.init_app(
        app,
        login_form=StarlitLoginForm,
        forgot_password_form=StarlitRecoverPasswordForm,
        datastore=user_datastore)
    app.before_request(security_processer)
