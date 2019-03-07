from flask import flash
from flask_admin.contrib.sqla.fields import QuerySelectMultipleField
from flask_security.forms import (
    RegisterForm,
    email_required,
    email_validator,
    unique_user_email,
    password_required,
    password_length,
    EqualTo,
)
from flask_security.confirmable import generate_confirmation_link
from flask_security.signals import user_registered
from flask_security.utils import (
    do_flash,
    get_message,
    send_mail,
    encrypt_password,
    config_value,
)
from wtforms.fields import StringField, SelectField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import data_required, ValidationError
from flask import current_app
from oy.babel import lazy_gettext
from oy.models import db, Role


def unique_username(form, field):
    from oy.boot.security import user_datastore

    if user_datastore.get_user(field.data) is not None:
        raise ValidationError(lazy_gettext("User name already exists"))


class OyRegisterForm(RegisterForm):
    user_name = StringField(
        label=lazy_gettext("User Name"),
        description=lazy_gettext("Should be UNIQUE"),
        validators=[data_required(), unique_username],
        render_kw=dict(required=True),
    )
    email = EmailField(
        label=lazy_gettext("User Email"),
        description=lazy_gettext(
            "An active email address, a confirmation link will be sent to it."
        ),
        validators=[email_required, email_validator, unique_user_email],
        render_kw=dict(required=True),
    )
    password = PasswordField(
        label=lazy_gettext("Password"),
        description=lazy_gettext("Not less than 6 characters"),
        validators=[password_required, password_length],
        render_kw=dict(required=True),
    )
    password_confirm = PasswordField(
        label=lazy_gettext("Re-Type Password"),
        validators=[EqualTo("password", message="RETYPE_PASSWORD_MISMATCH")],
        render_kw=dict(required=True),
    )
    roles = QuerySelectMultipleField(
        label=lazy_gettext("User Roles"),
        allow_blank=True,
        blank_text=lazy_gettext("No Roles"),
        query_factory=lambda: Role.query,
    )
    send_confirmation = BooleanField(
        label=lazy_gettext("Require email confirmation"),
        description=lazy_gettext(
            "we will not activate this account untill the user confirms his/her email address"
        ),
        default=True,
    )
