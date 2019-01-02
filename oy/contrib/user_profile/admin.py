from collections import OrderedDict
from flask import current_app, request, url_for, flash, redirect
from flask_security import current_user
from flask_admin import expose
from flask_admin import form
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView

from oy.boot.sqla import db
from oy.boot.security import user_datastore
from oy.babel import gettext, lazy_gettext
from oy.models.user import User
from oy.dynamicform import DynamicForm
from oy.contrib.admin.wrappers import OyModelView
from .models import Profile


class ProfileAdmin(OyModelView):
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
        profile_fields = current_app.data["profile_fields"]
        for name, ufield in DynamicForm(profile_fields).fields:
            rv.setdefault(f"profile_extra__{name}", ufield)
        return rv


def register_admin(app, admin):
    admin.add_view(
        ProfileAdmin(
            Profile,
            db.session,
            name=lazy_gettext("Profiles"),
            menu_icon_type="fa",
            menu_icon_value="fa-user",
        )
    )
