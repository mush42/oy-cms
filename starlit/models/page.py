# -*- coding: utf-8 -*-
"""	
    starlit.models.page
    ~~~~~~~~~~

    Provides the concrete Page model to be extended by other models

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from starlit.boot.sqla import db
from starlit.models.abstract import AbstractPage


class Page(AbstractPage):
    id = db.Column(db.Integer, primary_key=True)
    __contenttype__ = "page"
