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
from starlit.globals import current_page
from starlit.boot.exts.sqla import db

from starlit.util.dynamicform import DynamicForm
from starlit.util.helpers import date_stamp
from .models import FormEntry, FieldEntry, Form, Field

form = StarlitModule('form',
    __name__,
    static_folder="static",
    template_folder="templates",
    builtin=True
  )



def store_form(form):
    entry = FormEntry(form_id=current_page.id)
    for f in form:
        field = Field.query.filter_by(form_id=current_page.id).filter_by(name=f.name).one_or_none()
        if field is None:
            continue
        field_entry = FieldEntry(field_id=field.id)
        data = f.data
        if field.type == 'file_input':
            file_data = request.files[field.name]
            filename = '%s-%s-%s.%s' %(field.name, date_stamp(), str(time.time()).replace('.', ''), os.path.splitext(file_data.filename)[-1])
            path = os.path.join(current_app.config['FORM_UPLOADS_PATH'], secure_filename(filename))
            file_data.save(path)
            data = filename
        field_entry.value = data
        db.session.add(field_entry)
        entry.fields.append(field_entry)
    db.session.add(entry)
    db.session.commit()


@form.contenttype_handler('form', methods=['GET', 'POST'])
def form_view():
    form = DynamicForm(current_page.fields).form
    if form.validate_on_submit():
        store_form(form)
        flash(current_page.submit_message, 'markup')
        return redirect(request.path)
    return dict(form=form)
    
