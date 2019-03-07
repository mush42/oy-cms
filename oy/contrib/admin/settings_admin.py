# -*- coding: utf-8 -*-
"""
    oy.contrib.admin.core.settings
    ~~~~~~~~~~~~~~~~
    
    Admin module for the editable settings features
"""

import math
from itertools import chain
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app, request, flash, url_for, redirect
from flask_security import current_user
from flask_admin import expose
from flask_wtf import Form

from oy.boot.sqla import db
from oy.dynamicform import DynamicForm
from oy.babel import gettext, lazy_gettext
from oy.core.settings import SettingsProfile, current_settings
from .wrappers import OyModelView, AuthenticationViewMixin, OyBaseView


def active_formatter(view, context, model, name):
    if getattr(model, name):
        return gettext("Yes")
    return gettext("No")


class SettingsProfileAdmin(OyModelView):
    """TODO: a potential for multi site installation of oy?"""

    can_view_details = False
    can_create = False
    can_edit = False
    can_delete = False


def make_settings_form_for_category(app, category):
    fields = []
    for field in app.provided_settings_dict[category]:
        setting = field.asdict()
        setting["default"] = getattr(current_settings, setting["name"])
        fields.append(setting)
    return DynamicForm(fields).form


def update_settings_from_form(data):
    for k, v in data.items():
        if k == "csrf_token":
            continue
        current_settings.edit(k, v)


def register_settings_admin(app, admin):
    settings_category = gettext("Settings")
    admin.category_menu_orders[settings_category] = 200
    categories = set()
    for order, (category, settings) in enumerate(app.provided_settings):

        class SettingsAdmin(OyBaseView):
            settings_category = category

            def is_accessible(self):
                return super().is_accessible() and current_user.has_role("admin")

            @expose("/", methods=["Get", "POST"])
            def index(self):
                form = make_settings_form_for_category(
                    app, category=self.settings_category
                )
                if form.validate_on_submit():
                    update_settings_from_form(form.data)
                    flash("Settings were successfully saved")
                    return redirect(request.url)
                return self.render("admin/oy/settings.html", form=form)

        admin.add_view(
            SettingsAdmin(
                name=category.args["viewable_name"],
                category=settings_category,
                endpoint="admin-settings-{}".format(category),
                url="settings/{}".format(category),
                menu_order=order,
            )
        )
