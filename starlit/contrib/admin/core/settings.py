# -*- coding: utf-8 -*-
"""
    starlit.contrib.admin.core.settings
    ~~~~~~~~~~~~~~~~
    
    Admin module for the editable settings features
"""
from itertools import chain
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app, request, flash, url_for, redirect
from flask_admin import expose
from flask_wtf import Form

from starlit.boot.sqla import db
from starlit.dynamicform import DynamicForm
from starlit.babel import gettext, lazy_gettext
from starlit.core.settings import SettingsProfile, current_settings
from starlit.contrib.admin.wrappers import (
    StarlitModelView,
    AuthenticationViewMixin,
    StarlitBaseView,
)


def active_formatter(view, context, model, name):
    if getattr(model, name):
        return gettext("Yes")
    return gettext("No")


class SettingsProfileAdmin(StarlitModelView):
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
        setting.default = getattr(current_settings, setting.name)
        fields.append(setting)
    return DynamicForm(fields).form


def update_settings_from_form(data):
    for k, v in data.items():
        if k == "csrf_token":
            continue
        current_settings.edit(k, v)


def register_settings_admin(app, admin):
    admin.add_view(
        SettingsProfileAdmin(
            SettingsProfile,
            db.session,
            name=lazy_gettext("Settings Profiles"),
            category=gettext("Settings"),
            menu_icon_type="fa",
            menu_icon_value="fa-flag",
        )
    )
    categories = set()
    for category, settings in app.provided_settings:

        class SettingsAdmin(StarlitBaseView):
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
                return self.render("starlit_admin/settings.html", form=form)

        admin.add_view(
            SettingsAdmin(
                name=category.args["viewable_name"],
                menu_icon_type="fa",
                menu_icon_value="fa-gear",
                category=gettext("Settings"),
                endpoint="admin-settings-{}".format(category),
                url="settings/{}".format(category),
            )
        )
