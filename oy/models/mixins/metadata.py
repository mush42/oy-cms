# -*- coding: utf-8 -*-
"""	
    oy.models.mixins.metadata
    ~~~~~~~~~~

    Provides content meta-data mixin classes

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.boot.sqla import db
from ._sqlaevent import SQLAEvent


class Metadata(SQLAEvent):
    """Provides metadata about a specific piece of content."""

    meta_title = db.Column(
        db.Unicode(255),
        default="",
        info=dict(label="Meta Title", description="The title used by search engines"),
    )
    meta_description = db.Column(
        db.UnicodeText,
        default="",
        info=dict(
            label="Meta Description",
            description="The description used by search engines",
        ),
    )
    keywords = db.Column(
        db.Text,
        default="",
        info=dict(
            label="Keywords",
            description="The keywords for this content (Used by search engines)",
        ),
    )
    should_auto_generate = db.Column(
        db.Boolean,
        info=dict(
            label="Auto generate the metadata",
            description="If enabled the metadata will be generated automaticly",
        ),
    )

    def __get_meta_title__(self):
        return ""

    def __get_meta_description__(self):
        return ""

    def __get_keywords__(self):
        return ""

    def before_flush(self, session, is_modified):
        if self.should_auto_generate is None:
            self.should_auto_generate = True
        if not self.should_auto_generate:
            return
        cols = ["keywords", "meta_title", "meta_description"]
        state = db.inspect(self)
        for col in cols:
            state = db.inspect(self)
            if state.attrs[col].history.unchanged:
                continue
            func = getattr(self, f"__get_{col}__", None)
            if callable(func):
                setattr(self, col, func())
