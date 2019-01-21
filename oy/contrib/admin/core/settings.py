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
from flask_admin import expose
from flask_wtf import Form

from oy.boot.sqla import db
from oy.dynamicform import DynamicForm
from oy.babel import gettext, lazy_gettext
from oy.core.settings import SettingsProfile, current_settings
from oy.contrib.admin.wrappers import OyModelView, AuthenticationViewMixin, OyBaseView


def active_formatter(view, context, model, name):
    if getattr(model, name):
        return gettext("Yes")
    return gettext("No")


class SettingsProfileAdmin(OyModelView):
    can_view_details = True
    # Edit in a dialog not in a new page.
    edit_modal = True
    details_modal = True
    # Enable CSRF protection.
    form_excluded_columns = ["settings"]
    # How many entries to display per page?
    page_size = 5
    # Column formatters.
    column_formatters = {"is_active": active_formatter}
    column_default_sort = ("is_active", True)
    column_editable_list = ["name"]


def make_settings_form_for_category(app, category):
    fields = []
    for setting in app.provided_settings_dict[category]:
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
    admin.add_view(
        SettingsProfileAdmin(
            SettingsProfile,
            db.session,
            name=lazy_gettext("Settings Profiles"),
            category=settings_category,
            menu_icon_type="fa",
            menu_icon_value="fa-flag",
            menu_order=math.inf
        )
    )
    categories = set()
    for order, (category, settings) in enumerate(app.provided_settings):

        class SettingsAdmin(OyBaseView):
            settings_category = category

            @expose("/", methods=["Get", "POST"])
            def index(self):
                form = make_settings_form_for_category(
                    app, category=self.settings_category
                )
                if form.validate_on_submit():
                    update_settings_from_form(form.data)
                    flash("Settings were successfully saved")
                    return redirect(request.url)
                return self.render("oy_admin/settings.html", form=form)

        admin.add_view(
            SettingsAdmin(
                name=category.args["viewable_name"],
                menu_icon_type="fa",
                menu_icon_value="fa-gear",
                category=settings_category,
                endpoint="admin-settings-{}".format(category),
                url="settings/{}".format(category),
                menu_order=order
            )
        )
