# -*- coding: utf-8 -*-
"""
    oy.contrib.richtext_page.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides sqlalchemy models for the rich-text page contenttype.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from flask import current_app
from oy.models import db
from oy.models.page import Page


class RichTextPage(Page):
    __contenttype__ = "richtext_page"
    __metadescription_column__ = "content"

    id = db.Column(db.Integer, db.ForeignKey("page.id"), primary_key=True)
    content = db.deferred(db.Column(
        db.UnicodeText,
        nullable=False,
        info=dict(
            label="Content", description="Page content", mimetype="text/html"
        )
    ))
