from collections import namedtuple
from flask import current_app, request, g, abort
from starlit.wrappers import StarlitModule


class PageModule(StarlitModule):
    _page_handlers = None
    handler_opts = namedtuple('PageHandler', 'view_func methods')
    
    def __init__(self, *args, **kwargs):
        super(PageModule, self).__init__(*args, **kwargs)
        self._page_handlers = {}

    def add_handler(self, func, contenttype, methods=('GET',)):
        self._page_handlers[contenttype] = self.handler_opts(func, methods)

    def get_handler_for(self, contenttype):
        return self._page_handlers.get(contenttype)

    def handler(self, contenttype, methods):
        def wrapper(func):
            self.add_handler(func, contenttype, methods)
            def wrapped(*a, **kw):
                return func(*a, **kw)
            return wrapped
        return wrapper
