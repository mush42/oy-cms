from sqlalchemy.exc import SQLAlchemyError
from flask import current_app, request, flash, url_for, redirect
from flask_admin import BaseView, expose
from flask_wtf import Form

from starlit.boot.exts.sqla import db
from starlit.util.dynamicform import DynamicForm
from starlit_admin.core import AuthenticationViewMixin
from starlit_admin.plugin import AdminPlugin
from starlit.babel import gettext, lazy_gettext
from starlit.modules.editable_settings import current_settings


def make_settings_form_for_category(category):
    fields = []
    for option in current_app.provided_settings():
        if option.category != category:
            continue
        option.default = getattr(current_settings, option.name)
        fields.append(option)
    return DynamicForm(fields, with_admin=True).form


def update_settings_from_form(data):
    for k, v in data.items():
        if k == "csrf_token":
            continue
        current_settings.edit(k, v)


@AdminPlugin.setupmethod
def add_settings_categories(app, admin):
    categories = []
    for i in app.provided_settings():
        categories.append(i.category)
    for category in categories:
        class SettingsAdmin(AuthenticationViewMixin, BaseView):
            settings_category = category
            @expose('/', methods=['Get', 'POST'])
            def index(self):
                form = make_settings_form_for_category(category=self.settings_category)
                if form.validate_on_submit():
                    update_settings_from_form(form.data)
                    flash("Settings were successfully saved")
                    return redirect(request.url)
                return self.render('starlit_admin/settings.html', form=form)
        category_details = app.config["DEFAULT_SETTINGS_CATEGORIES"][category]
        admin.add_view(SettingsAdmin(
            name=category_details["label"],
            menu_icon_type='fa',
            menu_icon_value=category_details["icon"],
            category=gettext("Settings"),
            endpoint="admin-settings-{}".format(category),
            url="settings/{}".format(category)
        ))
