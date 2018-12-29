# -*- coding: utf-8 -*-
"""
    oy.globals
    ~~~~~~~~~~

    Oy context bound objects to be used during request handling.
    The most important one is the **current_page** which points to
    the currently requested page if there is one.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from werkzeug.local import LocalProxy
from flask import current_app, request
from oy.models.page import Page


def _get_page_for_request():
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
    return Page.query.filter(Page.slug_path == requested_slug_path).one_or_none()


current_page = LocalProxy(lambda: _get_page_for_request())
