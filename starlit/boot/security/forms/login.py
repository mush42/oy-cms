from flask import current_app
from flask_security.forms import LoginForm
from wtforms.fields import StringField, SelectField, PasswordField
from wtforms.validators import data_required
from starlit.babel import lazy_gettext

class EmailFormMixin(object):
    email = StringField(
        label=lazy_gettext('Email or Username'),
        validators=[data_required()],
        render_kw=dict(required=True)
    )

class PasswordFormMixin(object):
    password = PasswordField(
        label=lazy_gettext('Password'),
        validators=[data_required()],
        render_kw=dict(required=True)
    )

class StarlitLoginForm(EmailFormMixin, PasswordFormMixin, LoginForm):
    def __init__(self, *a, **kw):
        super(StarlitLoginForm, self).__init__(*a, **kw)
        self.lang.choices = current_app.config['SUPPORTED_LOCALES'].items()
    lang = SelectField(
        label=lazy_gettext('Dashboard Language'),
        validators=[data_required()],
        render_kw=dict(required=True)
    )

