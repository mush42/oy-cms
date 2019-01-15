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
from oy.boot.sqla import db
from oy.babel import lazy_gettext

from .slugged import Titled, Slugged
from .metadata import Metadata
from .publishable import Publishable
from .user_related import UserRelated


class Displayable(db.Model, Slugged, Titled, Metadata, Publishable, UserRelated):
    """The core of all oy content models"""

    __abstract__ = True
    __slugcolumn__ = "title"
    __keywordscolumn__ = "title"
    __metatitle_column__ = "title"
