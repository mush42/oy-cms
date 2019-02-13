from functools import wraps
from flask import request, redirect, url_for, abort
from flask_admin import Admin, expose, BaseView
from flask_admin.base import BaseView, AdminIndexView
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView, form
from flask_security import current_user
from oy.boot.sqla import db
from oy.babel import gettext, lazy_gettext


class AuthenticationViewMixin:
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role("admin"):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for("security.login", next=request.url))


class OyModelFormConverter(form.AdminModelConverter):
    def _get_label(self, name, field_args):
        info = getattr(self.view.model, name).info
        if info.get("label"):
            return info["label"]
        return super(OyModelFormConverter, self)._get_label(name, field_args)

    def _get_description(self, name, field_args):
        info = getattr(self.view.model, name).info
        if info.get("description"):
            return info["description"]
        return super(OyModelFormConverter, self)._get_description(name, field_args)


class OyModelView(AuthenticationViewMixin, ModelView):
    """Automatic authentication and some extras"""

    model_form_converter = OyModelFormConverter

    def get_column_name(self, field):
        if self.column_labels and field in self.column_labels:
            return self.column_labels[field]
        column = self.model.__mapper__.columns.get(field)
        if column is not None and column.info.get("label"):
            return column.info["label"]
        return super(OyModelView, self).get_column_name(field)


class OyIndexView(AuthenticationViewMixin, AdminIndexView):
    @expose("/")
    def index(self):
        return super(OyIndexView, self).index()


class OyBaseView(BaseView, AuthenticationViewMixin):
    pass


def admin_required(f):
    @wraps(f)
    def _decorated(*args, **kw):
        if not AuthenticationViewMixin().is_accessible():
            abort(404)
        return f(*args, **kw)

    return _decorated
