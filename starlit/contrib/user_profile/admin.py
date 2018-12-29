from collections import OrderedDict
from flask import current_app, request, url_for, flash, redirect
from flask_security import current_user
from flask_admin import expose
from flask_admin import form
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView

from starlit.boot.sqla import db
from starlit.boot.security import user_datastore
from starlit.babel import gettext, lazy_gettext
from starlit.models.user import User
from starlit.dynamicform import DynamicForm
from starlit.contrib.admin.wrappers import StarlitModelView
from .models import Profile


class BaseUserAdmin(StarlitModelView):
    def is_accessible(self):
        if super().is_accessible():
            return current_user.has_role("admin")
        return False


class ProfileAdmin(BaseUserAdmin):
    can_create = False
    can_delete = False
    column_exclude_list = ["user", "created", "extras"]
    column_list = ["first_name", "last_name", "updated"]
    form_excluded_columns = ["user", "extras", "updated", "created"]

    def on_form_prefill(self, form, id):
        model = self.get_one(id)
        for field in form:
            if field.name.startswith("profile_extra__"):
                field.data = model.get(field.name[15:])

    def after_model_change(self, form, model, is_created):
        for field in form:
            if field.name.startswith("profile_extra__"):
                model[field.name[15:]] = field.data
        db.session.commit()

    @property
    def form_extra_fields(self):
        """Contribute the fields of profile extras"""
        rv = {}
        profile_fields = current_app.data['profile_fields']
        for field in DynamicForm(profile_fields).fields:
            rv.setdefault(f"profile_extra__{field.name}")
        return rv


def register_admin(app, admin):
    with app.app_context():
        admin.add_view(
            ProfileAdmin(
                Profile,
                db.session,
                name=lazy_gettext("Profiles"),
                menu_icon_type="fa",
                menu_icon_value="fa-user",
            )
        )
