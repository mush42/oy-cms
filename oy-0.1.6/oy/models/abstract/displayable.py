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
from oy.models.mixins.slugged import Titled
from oy.models.mixins.metadata import Metadata
from oy.models.mixins.published import Published
from oy.models.mixins.user_related import UserRelated


class Displayable(db.Model, Titled, Metadata, Published, UserRelated):
    """The core of all oy content models"""

    __abstract__ = True
    __slugcolumn__ = "title"
    __keywordscolumn__ = "title"
    __metatitle_column__ = "title"

    @declared_attr
    def contenttype(cls):
        return db.Column(db.String(128), info=dict(label="Type"))

    @declared_attr
    def show_in_menu(cls):
        return db.Column(
            db.Boolean,
            default=True,
            info=dict(
                label="Show in menu",
                description="Show this page in the navigation menus.",
            ),
        )

    @declared_attr
    def __mapper_args__(cls):
        return dict(
            polymorphic_identity=cls.__contenttype__, polymorphic_on=cls.contenttype
        )
