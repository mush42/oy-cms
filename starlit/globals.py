import sys
from werkzeug import import_string
from werkzeug.local import LocalProxy
from flask import g, current_app, request


def _get_page_cls():
    cls_import_name = current_app.config['PARENT_PAGE_CLASS']
    if cls_import_name in sys.modules:
        return sys.modules[cls_import_name]
    return import_string(cls_import_name)


parent_page_class = LocalProxy(lambda: _get_page_cls())


def _get_page_for_request():
    cls = parent_page_class
    if request is None:
        raise RuntimeError("Working outside of request context.")
    requested_slug_path = request.path.strip('/')
    if requested_slug_path is None:
        return
    requested_slug_path = requested_slug_path or current_app.config['HOME_SLUG']
    return cls.query.filter(cls.slug_path==requested_slug_path).one()

current_page = LocalProxy(lambda: _get_page_for_request())