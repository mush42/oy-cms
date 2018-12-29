# -*- coding: utf-8 -*-
"""
    starlit.contrib.form.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides a custom page contenttype.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import time
import os.path
from flask import (
    current_app,
    request,
    make_response,
    redirect,
    render_template,
    url_for,
    abort,
    flash,
)
from werkzeug import secure_filename
from flask_wtf import Form as HtmlForm
from starlit.globals import current_page
from starlit.boot.sqla import db
from starlit.contrib.extbase import StarlitExtBase
from starlit.dynamicform import DynamicForm
from starlit.helpers import date_stamp
from .admin import register_admin
from . import models


class Form(StarlitExtBase):
    """Extenssion entry point for starlit forms."""

    module_args = dict(
        name="starlit.contrib.form",
        import_name="starlit.contrib.form",
        static_folder="static",
        template_folder="templates"
    )

    def init_app(self, app):
        app.add_contenttype_handler(
            "form", self.form_view, methods=("GET", "POST"), module="form"
        )

    def store_form(self, form):
        entry = FormEntry(form_id=current_page.id)
        for f in form:
            field = (
                Field.query.filter_by(form_id=current_page.id)
                .filter_by(name=f.name)
                .one_or_none()
            )
            if field is None:
                continue
            field_entry = FieldEntry(field_id=field.id)
            data = f.data
            if field.type == "file_input":
                file_data = request.files[field.name]
                filename = "%s-%s-%s.%s" % (
                    field.name,
                    date_stamp(),
                    str(time.time()).replace(".", ""),
                    os.path.splitext(file_data.filename)[-1],
                )
                filename = secure_filename(filename)
                path = os.path.join(current_app.config["FORM_UPLOADS_PATH"], filename)
                file_data.save(path)
                data = filename
            field_entry.value = data
            db.session.add(field_entry)
            entry.fields.append(field_entry)
        db.session.add(entry)
        db.session.commit()

    def form_view(self):
        form = DynamicForm(current_page.fields).form
        if form.validate_on_submit():
            self.store_form(form)
            flash(current_page.submit_message, "success")
            return redirect(request.path)
        return dict(form=form)
