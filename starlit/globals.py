from werkzeug import import_string
from werkzeug.local import LocalProxy
from flask import g, current_app, request, _request_ctx_stack


def _get_page_cls():
    cls_import_name = app.config['PARENT_PAGE_CLASS']
    if cls_import_name in sys.modules:
        return sys.modules[cls_import_name]
    return import_string(cls_import_name)


parent_page_class = LocalProxy(lambda: _get_page_cls())


def _get_page_for_request():
    cls = parent_page_class
    ctx = _request_ctx_stack.top
    if ctx is None:
        raise RuntimeError("Working outside of request context.")
    elif getattr(ctx, 'requested_slug_path', None) is None:
        return
    requested_slug_path = ctx.requested_slug_path or current_app.config['HOME_SLUG']
    return cls.query.filter(cls.slug_path==requested_slug_path).one()

current_page = LocalProxy(lambda: _get_page_for_request())