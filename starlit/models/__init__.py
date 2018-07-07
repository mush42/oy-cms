# -*- coding: utf-8 -*-
"""	
    starlit.models
    ~~~~~~~~~~

    Provides abstract and mixin :mod:`sqlalchemy` classes that are the core
    building blocks of any content management system.

    Another interesting functionality is the :class:`SQLAEvent` which provides
    a convenient mechanism to hook into sqlalchemy life cycle events. 

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from starlit.boot.sqla import db
from .events import *
from .user import *
from .settings import *