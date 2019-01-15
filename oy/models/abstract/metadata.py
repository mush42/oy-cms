# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.metadata
    ~~~~~~~~~~

    Provides content meta-data mixin classes

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.boot.sqla import db
from ._sqlaevent import SQLAEvent


class Orderable(SQLAEvent):
    """Provide an ordering field."""

    order = db.Column(db.Integer)

    def after_flush(self, session, is_modified):
        if is_modified:
            if 'parent' not in db.inspect(self).unmodified:
                self.order = None

    def after_flush_postexec(self, session, is_modified):
        if self.order:
            return
        cls = self.__class__
        sel = db.select([db.func.max(cls.order)])
        if self.parent_id:
            sel = sel.where(cls.parent_id == self.parent_id)
        res = session.execute(sel).fetchone()[0]
        if res is None:
            res = 0
        self.order = res + 1


class Metadata(Orderable):
    """Provides metadata about a specific piece of content."""

    meta_title = db.Column(
        db.Unicode(255),
        default=u"",
        info=dict(label="Meta Title", description="The title used by search engines"),
    )
    meta_description = db.Column(
        db.UnicodeText,
        default=u"",
        info=dict(
            label="Meta Description",
            description="The description used by search engines",
        ),
    )
    should_auto_generate = db.Column(
        db.Boolean,
        info=dict(
            label="Auto generate the metadata",
            description="If enabled the metadata will be generated automaticly",
        ),
    )
    keywords = db.Column(
        db.Text,
        default=u"",
        info=dict(
            label="Keywords",
            description="The keywords for this content (Used by search engines)",
        ),
    )

    @property
    def options(self):
        options = (
            ("meta_title", getattr(self, "__metatitle_column__", None), None),
            (
                "meta_description",
                getattr(self, "__metadescription_column__", None),
                None,
            ),
            ("keywords", getattr(self, "__keywordscolumn__", None), self.gen_keywords),
        )
        return (opt for opt in options if opt[1])

    def gen_keywords(self, value):
        return " ".join(value.split())

    def set_value(self, attrname, colname, genfunc):
        if not getattr(self, attrname):
            value = getattr(self, colname)
            if genfunc:
                value = genfunc(value)
            setattr(self, attrname, value)

    def gen_all_values(self):
        if not self.should_auto_generate:
            return
        for attrname, colname, genfunc in self.options:
            self.set_value(attrname, colname, genfunc)

    def before_flush(self, session, is_modified):
        if is_modified:
            state = db.inspect(self)
            for attrname, colname, genfunc in self.options:
                if colname not in state.unmodified:
                    self.set_value(attrname, colname, genfunc)
        else:
            self.gen_all_values()

    def on_init(self):
        if self.should_auto_generate is None:
            self.should_auto_generate = True
