# -*- coding: utf-8 -*-
"""	
    starlit.models.abstract.metadata
    ~~~~~~~~~~

    Provides content meta-data mixin classes

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy import inspect
from starlit.boot.exts.sqla import db
from starlit.util.helpers import make_summary
from ._sqlaevent import SQLAEvent


class Metadata(SQLAEvent):
    """Provides fields which could be used with HTML meta tags"""
    meta_title = db.Column(
        db.Unicode(255),
        default=u'',
        info=dict(
            label='Meta Title',
            description='The title used by search engines'
        )
    )
    meta_description = db.Column(
        db.UnicodeText,
        default=u'',
        info=dict(
            label='Meta Description',
            description='The description used by search engines'
        )
    )
    should_auto_generate = db.Column(
        db.Boolean,
        info=dict(
            label='Auto generate the metadata',
            description='If enabled the metadata will be generated automaticly'
        )
    )
    keywords = db.Column(
        db.Text, 
        default=u'',
        info=dict(
            label='Keywords',
            description='The keywords for this content (Used by search engines)'
        )
    )

    @property
    def options(self):
        options = (
            ('meta_title', getattr(self, '__metatitle_column__', None), None),
            ('meta_description', getattr(self, '__metadescription_column__', None), self.gen_description),
            ('keywords', getattr(self, '__keywordscolumn__', None), self.gen_keywords),
        )
        return (opt for opt in options if opt[1])

    def gen_keywords(self, value):
        return ' '.join(value.split())

    def gen_description(self, value):
        return make_summary(value)

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
            state = inspect(self)
            for attrname, colname, genfunc in self.options:
                if colname not in state.unmodified:
                    self.set_value(attrname, colname, genfunc)
        else:
            self.gen_all_values()

    def on_init(self):
        if self.should_auto_generate is None:
            self.should_auto_generate = True
