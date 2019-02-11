# -*- coding: utf-8 -*-
"""	
    oy.models.page
    ~~~~~~~~~~

    Provides the concrete Page model to be extended by other models

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from datetime import datetime
from sqlalchemy_utils import observes
from flask_sqlalchemy import BaseQuery
from oy.boot.sqla import db
from oy.models.abstract import AbstractPage


class PageQuery(BaseQuery):
    """Add page specific filters to the query"""

    @property
    def roots(self):
        """Return only root pages."""
        return self.filter(Page.left == Page.get_default_level())

    @property
    def published(self):
        """Query only published pages."""
        sel = db.and_(
            Page.status == "published",
            Page.publish_date != None,
            db.or_(Page.expire_date == None, Page.expire_date > datetime.utcnow()),
        )
        return self.filter(sel)

    @property
    def viewable(self):
        return self.published.order_by(Page.tree_id.desc())

    @property
    def menu_pages(self):
        return self.roots.viewable.filter(Page.show_in_menu == True)


class Page(AbstractPage):
    """The concrete Page model."""

    __contenttype__ = "page"
    id = db.Column(
        db.Integer, db.Sequence("page_id_seq", start=1, increment=1), primary_key=True
    )
    query_class = PageQuery
