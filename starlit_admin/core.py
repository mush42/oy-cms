from flask import request, redirect, url_for, abort
from flask_admin import Admin, expose, BaseView
from flask_admin.base import BaseView, AdminIndexView
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView, form
from flask_security import current_user
from starlit.boot.sqla import db
from starlit.babel import gettext, lazy_gettext

class AuthenticationViewMixin(object):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

class StarlitModelFormConvertor(form.AdminModelConverter):
    def _get_label(self, name, field_args):
        info = getattr(self.view.model, name).info
        if info.get('label'):
            return info['label']
        return super(StarlitModelFormConvertor, self)._get_label(name, field_args)

    def _get_description(self, name, field_args):
        info = getattr(self.view.model, name).info
        if info.get('description'):
            return info['description']
        return super(StarlitModelFormConvertor, self)._get_description(name, field_args)


class StarlitModelView(AuthenticationViewMixin, ModelView):
    """Automatic authentication and some extras"""
    model_form_converter = StarlitModelFormConvertor
    def get_column_name(self, field):
        if self.column_labels and field in self.column_labels:
            return self.column_labels[field]
        column = self.model.__mapper__.columns.get(field)
        if column is not None and column.info.get('label'):
            return column.info['label']
        return super(StarlitModelView, self).get_column_name(field)

class StarlitIndexView(AuthenticationViewMixin, AdminIndexView):
    @expose('/')
    def index(self):
        return super(StarlitIndexView, self).index()



class StarlitBaseView(BaseView):
    def create_blueprint(self, admin):
        return super(StarlitBaseView, self).create_blueprint(admin)
