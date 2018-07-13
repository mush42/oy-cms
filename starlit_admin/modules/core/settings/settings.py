from itertools import chain
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app, request, flash, url_for, redirect
from flask_admin import expose
from flask_wtf import Form

from starlit.boot.sqla import db
from starlit.dynamicform import DynamicForm
from starlit.babel import gettext, lazy_gettext
from starlit.core.settings import current_settings
from starlit_admin.core import AuthenticationViewMixin, StarlitBaseView


def make_settings_form_for_category(category):
    fields = []
    opts = chain.from_iterable((opts for modname, opts in current_app.provided_settings))
    options = filter(lambda opt: opt.category == category, opts)
    for option in options:
        option['default'] = getattr(current_settings, option.name)
        fields.append(option)
    return DynamicForm(fields).form


def update_settings_from_form(data):
    for k, v in data.items():
        if k == "csrf_token":
            continue
        current_settings.edit(k, v)


