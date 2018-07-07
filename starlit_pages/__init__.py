from collections import namedtuple
from flask import current_app, request, _request_ctx_stack
from starlit_modules.page.globals import current_page, parent_page_class
from starlit.wrappers import StarlitModule
from starlit.plugin import StarlitPlugin
from starlit.util.option import Option
from starlit.babel import lazy_gettext
from .models import Page
from .templating import render_page_template


handler_opts = namedtuple('PageContentTypeHandler', 'view_func methods module')


def enject_pages():
    pages = parent_page_class.query.viewable.filter(
        parent_page_class.is_primary==True).filter(
        parent_page_class.slug_path!=current_app.config.get('HOME_SLUG')
    ).all()
    return dict(
        pages=pages,
        current_page=current_page,
        page=current_page
    )


class PagePlugin(StarlitPlugin):
    needs_module_registration
    blueprint_opts = dict(
        name='page-plugin',
        import_name=__name__,
        static_folder="static",
        template_folder="templates",
    )

    def __init__(self, app=None, *args, **kwargs):
        super(PagePlugin, self)/__init__(app, *args, **kwargs)
        self.contenttype_handlers = {}

    def init_app(self, app, *args, **kwargs):
        super(PagePlugin, self).init_app(app, *args, **kwargs)
        app.before_request_funcs.setdefault(None, []).append(self.set_page_and_response_if_appropriate)
        app.template_context_processors[None].append(self.enject_pages)

    def page_view(self):
        handler = self.get_handler_for(current_page.contenttype)
        template_args = {}
        if handler is not None:
            _request_ctx_stack.top.module = handler.module
            if request.method not in handler.methods:
                abort(405)
            rv = handler.view_func()
            if isinstance(rv, dict):
                template_args.update(rv)
            else:
                return rv
        return render_page_template(context=template_args)

    def set_page_and_response_if_appropriate(self):
        if isinstance(request.routing_exception, NotFound) and current_page:
            return self.page_view()

    def _add_contenttype_handler(self, contenttype, view_func, methods=('GET',), module=None):
        self.contenttype_handlers[contenttype] = handler_opts(
            view_func,
            methods,
            module
            )

    def contenttype_handler(self, contenttype, methods):
        """A decorator to add custom contenttype handlers to be
        registered with the application

        .. Note::
            Functions decorated with this functions are treated like
            flask views in terms of their return values.

        :param contenttype: a string that identify a certain page class
        :param methods: a list of HTTP methods that are accepted by this handler
        """
        def wrapper(func):
            self._add_contenttype_handler(func, contenttype, methods)
            def wrapped(*a, **kw):
                return func(*a, **kw)
            return wrapped
        return wrapper

    def get_handler_for(self, contenttype):
        return self.contenttype_handlers.get(contenttype)

