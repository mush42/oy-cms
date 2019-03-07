# -*- coding: utf-8 -*-
"""	
    oy.models
    ~~~~~~~~~~

    Provides abstract and mixin :mod:`sqlalchemy` models that are
    the core building blocks of any content management system.

    Another interesting functionality is the :class:`SQLAEvent` which provides
    a convenient mechanism to hook into sqlalchemy model life cycle events. 

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.boot.sqla import db
from . import _events
from .user import User, Role
from .settings import SettingsProfile, SettingCategory, Settings
from .page import Page, PageQuery
