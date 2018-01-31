from flask import current_app, request, g, abort
from starlit.wrappers import StarlitModule
from .models import Page


def get_page(slug_path):
    return Page.query.published.filter(Page.slug_path==slug_path).one_or_none()


class PageModule(StarlitModule):
    _page_handlers = None
    def __init__(self, *args, **kwargs):
        super(PageModule, self).__init__(*args, **kwargs)
        self._page_handlers = {}
        self.before_request(self.set_g_page)

    def add_handler(self, func, contenttype, methods):
        self._page_handlers[contenttype] = (func, methods)

    def get_handler_for(self, contenttype):
        return self._page_handlers.get(contenttype)

    def handler(self, contenttype, methods):
        def wrapper(func):
            self.add_handler(func, contenttype, methods)
            def wrapped(*a, **kw):
                return func(*a, **kw)
            return wrapped
        return wrapper

    def set_g_page(self):
        slug = request.path.strip('/')
        if not slug:
            slug = current_app.config.get('HOME_SLUG')
        slug_path = slug.split('/')
        while slug_path:
            g.page = get_page('/'.join(slug_path))
            if g.page:
                break
            slug_path.pop(-1)
        if g.page:
            setattr(g, g.page.__contenttype__, g.page)
