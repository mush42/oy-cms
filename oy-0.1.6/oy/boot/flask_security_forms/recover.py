from flask_security.forms import ForgotPasswordForm
from wtforms.fields.html5 import EmailField
from wtforms.validators import data_required, ValidationError
from oy.babel import lazy_gettext


class OyRecoverPasswordForm(ForgotPasswordForm):
    submit = None
    email = EmailField(
        label=lazy_gettext("Your registered email address"),
        validators=[data_required()],
        render_kw=dict(required=True),
    )
