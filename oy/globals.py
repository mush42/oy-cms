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
from flask import _app_ctx_stack, current_app, request
from flask.globals import _request_ctx_err_msg
from oy.models.page import Page


def _get_page_for_request():
    if not request:
        raise RuntimeError(_request_ctx_err_msg)
    url_path = request.path.strip("/")
    if not url_path:
        return Page.query.filter_by(slug=current_app.config["HOME_SLUG"]).one()
    return Page.query.filter_by(url_path=url_path).one_or_none()


current_handler = LocalProxy(lambda: getattr(_app_ctx_stack.top, "handler", None))
current_page = LocalProxy(lambda: _get_page_for_request())
