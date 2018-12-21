# -*- coding: utf-8 -*-
"""
    starlit.contrib.form.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides sqlalchemy models for the form contenttype.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.orm import validates
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app
from starlit.models import db
from starlit.models.abstract import TimeStampped
from starlit.models.abstract import ProxiedDictMixin, DynamicProp
from starlit.babel import lazy_gettext
from starlit.models.page import Page


class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False,
        info=dict(
            label=lazy_gettext("Field Name"),
            description=lazy_gettext(
                "This is the same as the column name in the resulting data. It should contain only letters, numbers, and under scors, and should not start with a number"
            ),
        ),
    )
    label = db.Column(
        db.Unicode(255),
        nullable=False,
        info=dict(
            label=lazy_gettext("Field Label"),
            description=lazy_gettext("This will be shown to the users"),
        ),
    )
    description = db.Column(
        db.Unicode(255),
        default="",
        info=dict(
            label=lazy_gettext("Field Description"),
            description=lazy_gettext("A summary about the field"),
        ),
    )
    type = db.Column(db.String(50),
        nullable=False,
        info=dict(
            label=lazy_gettext("Field Type"),
            description=lazy_gettext("HTML Type of the field"),
        ),
    )
    choices = db.Column(
        db.Unicode,
        info=dict(
            label=lazy_gettext("Field Choices"),
            description=lazy_gettext("If it is a select"),
        ),
    )
    default = db.Column(
        db.Unicode,
        info=dict(
            label=lazy_gettext("Default Value"),
            description=lazy_gettext("Default value to populate the field"),
        ),
    )
    required = db.Column(
        db.Boolean,
        default=False,
        info=dict(
            label=lazy_gettext("Required"),
            description=lazy_gettext("Whether this field is required or not"),
        ),
    )
    max_length = db.Column(
        db.Integer,
        default=255,
        info=dict(
            label=lazy_gettext("Maximom Length"),
            description=lazy_gettext("Max number of chars the user can enter"),
        ),
    )
    form_id = db.Column(db.Integer, db.ForeignKey("form.id"))

    @validates("type")
    def validate_field_type(self, key, ftype):
        # Bypass validation to be able to install fixtures
        if not current_app._got_first_request:
            return ftype
        if ftype not in current_app.available_field_types:
            raise ValueError("Field type is not supported.")
        return ftype
    

class Form(Page):
    __contenttype__ = "form"
    id = db.Column(db.Integer, db.ForeignKey("page.id"), primary_key=True)
    submit_text = db.Column(
        db.String(255),
        info=dict(
            label=lazy_gettext("Submit button text"),
            description=lazy_gettext("Text of the submit button in the form"),
        ),
    )
    submit_message = db.Column(
        db.UnicodeText,
        info=dict(
            label=lazy_gettext("After Submit Message"),
            description=lazy_gettext(
                "A Message to display for the user after submitting the form"
            ),
        ),
    )
    fields = db.relationship(Field, backref="form")


class FormEntry(TimeStampped, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey("form.id"))
    form = db.relationship("Form", backref="entries")


class FieldEntry(db.Model, DynamicProp):
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey(FormEntry.id))
    entry = db.relationship("FormEntry", backref="fields")
    field_id = db.Column(db.Integer, db.ForeignKey("field.id"))
    field = db.relationship("Field", backref="entries")
