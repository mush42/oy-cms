# -*- coding: utf-8 -*-
"""
    starlit.contrib.page.globals
    ~~~~~~~~~~

    Starlit context bound objects to be used during request handling.
    The most important one is the **current_page** which points to
    the currently requested page if there is one.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import sys
from werkzeug import import_string
from werkzeug.local import LocalProxy
from flask import current_app, request


def _get_page_cls():
    cls_import_name = current_app.config["PARENT_PAGE_CLASS"]
    if cls_import_name in sys.modules:
        return sys.modules[cls_import_name]
    return import_string(cls_import_name)


def _get_page_for_request():
    cls = parent_page_class
    if request is None:
        raise RuntimeError("Working outside of request context.")
    requested_slug_path = request.path
    blueprint = request.blueprint
    if blueprint is not None:
        requested_slug_path = requested_slug_path.lstrip(
            current_app.blueprints[blueprint].url_prefix or ""
        )
    requested_slug_path = requested_slug_path.strip("/")
    requested_slug_path = requested_slug_path or current_app.config["HOME_SLUG"]
    return cls.query.filter(cls.slug_path == requested_slug_path).one_or_none()


parent_page_class = LocalProxy(lambda: _get_page_cls())
current_page = LocalProxy(lambda: _get_page_for_request())
