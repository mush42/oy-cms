# -*- coding: utf-8 -*-
"""
    starlit.contrib.page
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides page models and templates
    as well as page rendering logic.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from collections import namedtuple
from werkzeug.exceptions import NotFound
from flask import current_app, request, _request_ctx_stack
from starlit.wrappers import StarlitModule
from starlit.babel import lazy_gettext
from .models import Page
from .globals import current_page, parent_page_class
from .templating import render_page_template
from .admin import register_admin


class Page(StarlitModule):
    """A starlit module that provide the extenssion
        point to the page functionality
    """
    
    # Holds info about a page handler
    handler_opts = namedtuple('PageContentTypeHandler', 'view_func methods module')

    def __init__(self, app,
          name='starlit.contrib.page',
          import_name='starlit.contrib.page',
          **kwargs):
        super().__init__(name,
            import_name=import_name,
            template_folder="templates",
            viewable_name=lazy_gettext("Page"),
            **kwargs)
        self.contenttype_handlers = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.before_app_request(self.set_page_and_response_if_appropriate)
        self.app_context_processor(self.enject_pages)
        app.register_module(self)

    def enject_pages(self):
        pages = parent_page_class.query.viewable.filter(
            parent_page_class.is_primary==True).filter(
            parent_page_class.slug_path!=current_app.config.get('HOME_SLUG')
        ).all()
        return dict(
            pages=pages,
            current_page=current_page,
            page=current_page
        )

    def page_view(self):
        handler = self.get_handler_for(current_page.contenttype)
        if handler is not None:
            _request_ctx_stack.top.module = handler.module
            if request.method not in handler.methods:
                abort(405)
            rv = handler.view_func()
            if isinstance(rv, dict):
                return render_page_template(context=rv)
            else:
                return rv

    def set_page_and_response_if_appropriate(self):
        if isinstance(request.routing_exception, NotFound) and current_page:
            return self.page_view()

    def _add_contenttype_handler(self, contenttype, view_func, methods=('GET',), module=None):
        self.contenttype_handlers[contenttype] = self.handler_opts(
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
            return func
        return wrapper

    def get_handler_for(self, contenttype):
        return self.contenttype_handlers.get(contenttype)

