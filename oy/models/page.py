# -*- coding: utf-8 -*-
"""	
    oy.models.page
    ~~~~~~~~~~

    Provides the concrete Page model to be extended by other models

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.boot.sqla import db
from oy.models.abstract import AbstractPage


class Page(AbstractPage):
    id = db.Column(db.Integer, primary_key=True)
    __contenttype__ = "page"
