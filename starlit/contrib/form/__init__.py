import time
import os.path
from flask import (
    current_app, request,
    make_response, redirect,
    render_template, url_for,
    abort, flash
  )
from werkzeug import secure_filename
from flask_wtf import Form as HtmlForm
from starlit.wrappers import StarlitModule
from starlit.contrib.page.globals import current_page
from starlit.boot.sqla import db
from starlit.dynamicform import DynamicForm
from starlit.helpers import date_stamp
from .models import Form, Field, FormEntry, FieldEntry



class Form(StarlitModule):
    """Extenssion entry point for starlit forms."""
    
    def __init__(self, app=None):
        super().__init__('starlit.contrib.form', __name__, template_folder='templates')
        if app:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, '_page_ext'):
            raise RuntimeError("Page extension has not been registered with the application.")
        app._page_ext.contenttype_handler(self.form_view)
        self.app.register_module(self)

    def store_form(self, form):
        entry = FormEntry(form_id=current_page.id)
        for f in form:
            field = Field.query.filter_by(form_id=current_page.id
                ).filter_by(name=f.name).one_or_none()
            if field is None:
                continue
            field_entry = FieldEntry(field_id=field.id)
            data = f.data
            if field.type == 'file_input':
                file_data = request.files[field.name]
                filename = '%s-%s-%s.%s' %(
                    field.name, date_stamp(),
                    str(time.time()).replace('.', ''),
                    os.path.splitext(file_data.filename)[-1])
                filename = secure_filename(filename)
                path = os.path.join(current_app.config['FORM_UPLOADS_PATH'], filename)
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
            store_form(form)
            flash(current_page.submit_message, 'success')
            return redirect(request.path)
        return dict(form=form)
        
