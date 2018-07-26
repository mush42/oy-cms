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
from flask import current_app, request, _request_ctx_stack
from starlit.contrib.page.globals import current_page, parent_page_class
from starlit.babel import lazy_gettext
from .resource_module import page_resource_module
from .models import Page
from .templating import render_page_template


# Holds info about a page handler
handler_opts = namedtuple('PageContentTypeHandler', 'view_func methods module')


class Page(object):
    """Flask extension for starlit pages."""

    # Resource module that provides templates and static files
    resource_module = page_resource_module

    def __init__(self, app=None):
        self.contenttype_handlers = {}
        if app:
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        app.before_request_funcs.setdefault(None, []).append(self.set_page_and_response_if_appropriate)

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
            return func
        return wrapper

    def get_handler_for(self, contenttype):
        return self.contenttype_handlers.get(contenttype)

