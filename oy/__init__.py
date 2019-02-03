# -*- coding: utf-8 -*-
"""
    oy
    ~~~~~~~~~~~~~~~~~~

    Oy is a Micro Content Management System (CMS) for the modern web.
    It is based on Flask, and provides a full-fledged and flexible CMS
    engine with a strong emphasis on flexibility for developers.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.wrappers import Oy, OyModule
from oy.prepare_app import prepare_app
from oy.views import ContentView
from oy.globals import current_page, current_handler
from oy.core.settings import current_settings_profile, current_settings


__author__ = "Musharraf Omer"
__version__ = "0.1"
