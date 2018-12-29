# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.displayable
    ~~~~~~~~~~

    This module provides the core content model for oy.
    Its core functionality is implemented by other mixin classes

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from flask import current_app
from flask_sqlalchemy import BaseQuery
from oy.boot.sqla import db
from oy.babel import lazy_gettext

from .slugged import Slugged, Titled
from .metadata import Metadata
from .publishable import Publishable
from .user_related import UserRelated


class DisplayableQuery(BaseQuery):
    """A Custom query that provides additional methods"""

    @property
    def published(self):
        pub = self._joinpoint_zero().columns["publish_date"]
        expire = self._joinpoint_zero().columns["expire_date"]
        rv = self.filter_by(status="published").filter(pub <= datetime.utcnow())
        if expire is not None:
            rv.filter(expire >= datetime.utcnow())
        return rv


class Displayable(db.Model, Titled, Slugged, Metadata, Publishable, UserRelated):
    """The core of all oy content models"""

    __abstract__ = True
    __slugcolumn__ = "title"
    __keywordscolumn__ = "title"
    __metatitle_column__ = "title"
    query_class = DisplayableQuery

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
