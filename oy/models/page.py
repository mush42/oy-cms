# -*- coding: utf-8 -*-
"""	
    oy.models.page
    ~~~~~~~~~~

    Provides the concrete Page model to be extended by other models

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from datetime import datetime
from flask_sqlalchemy import BaseQuery
from oy.boot.sqla import db
from oy.models.abstract import AbstractPage


class PageQuery(BaseQuery):
    """Add page specific filters to the query"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_qbundle = db.Bundle('minq',
            Page.id,
            Page.title,
            Page.slug,
            Page.slug_path
        )

    @property
    def minimal(self):
        return self.from_self(self.min_qbundle)

    @property
    def published(self):
        """Query only published pages."""
        sel = db.and_(
            Page.status == "published",
            db.or_(
                Page.expire_date == None,
                Page.expire_date > datetime.utcnow(),
            ),
        )
        return self.filter(sel)

    @property
    def viewable(self):
        return self.published.filter(Page.is_live == True)


class Page(AbstractPage):
    id = db.Column(db.Integer, primary_key=True)
    query_class = PageQuery
    __contenttype__ = "page"
