from flask import flash
from flask_admin.contrib.sqla.fields import QuerySelectMultipleField
from flask_security.forms import(
    RegisterForm,email_required,
    email_validator, unique_user_email,
    password_required, password_length,
    EqualTo,
)
from flask_security.confirmable import generate_confirmation_link
from flask_security.signals import user_registered
from flask_security.utils import do_flash, get_message, send_mail, encrypt_password, config_value
from wtforms.fields import StringField, SelectField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import data_required, ValidationError
from ... import app, db
from ...main import user_datastore
from ...babel import lazy_gettext, gettext
from ...user.models import Role


def unique_username(form, field):
    if user_datastore.get_user(field.data) is not None:
        raise ValidationError(lazy_gettext('User name already exists'))

class NewPasswordConfirmMixin(object):
    password = PasswordField(
        label=lazy_gettext('Password'),
        description=lazy_gettext('Not less than 6 characters'),
        validators=[password_required, password_length],
        render_kw=dict(required=True)
    )
    password_confirm = PasswordField(
        label=lazy_gettext('Re-Type Password'),
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH')],
        render_kw=dict(required=True)
    )

class UsernameEmailMixin(object):
    user_name = StringField(
        label=lazy_gettext('User Name'),
        description=lazy_gettext('Should be UNIQUE'),
        validators=[data_required(), unique_username],
        render_kw=dict(required=True)
    )
    email = EmailField(
        label=lazy_gettext('User Email'),
        description=lazy_gettext('An active email address, a confirmation link will be sent to it.'),
        validators=[email_required, email_validator, unique_user_email],
        render_kw=dict(required=True)
    )

class CanellaRegisterForm(UsernameEmailMixin, NewPasswordConfirmMixin, RegisterForm):
    submit = None
    roles = QuerySelectMultipleField(
        label=lazy_gettext('User Roles'),
        allow_blank=True,
        blank_text=lazy_gettext('No Roles'),
        query_factory=lambda: Role.query,
    )
    send_confirmation = BooleanField(
        label=lazy_gettext('Require email confirmation'),
        description=lazy_gettext('we will not activate this account untill the user confirms his/her email address'),
        default=True
    )

def register_user(should_confirm, **kwargs):
    confirmation_link, token = None, None
    kwargs['password'] = encrypt_password(kwargs['password'])
    user = user_datastore.create_user(**kwargs)
    user_datastore.commit()
    flash(gettext('User created successfully'))
    if should_confirm:
        confirmation_link, token = generate_confirmation_link(user)
        do_flash(*get_message('CONFIRM_REGISTRATION', email=user.email))
        send_mail(
            config_value('EMAIL_SUBJECT_REGISTER'),
            user.email, 'welcome', user=user, confirmation_link=confirmation_link)
    user_registered.send(app, user=user, confirm_token=token)
