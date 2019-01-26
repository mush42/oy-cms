# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.base_page
    ~~~~~~~~~~

    Provides an abstract Page model.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app
from oy.boot.sqla import db
from .displayable import Displayable
from .slugged import ScopedUniquelySlugged, MPSlugged
from .misc import SelfRelated, Orderable


class AbstractPage(
    Displayable, ScopedUniquelySlugged, MPSlugged, Orderable, SelfRelated
):
    """Extends :class:`Displayable` with special fields"""

    __abstract__ = True

    @property
    def url(self):
        return "/" + self.slug_path

    @hybrid_property
    def is_home(self):
        return self.slug == current_app.config["HOME_SLUG"]
