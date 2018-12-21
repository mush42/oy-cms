# -*- coding: utf-8 -*-
"""	
    starlit.content_renderer
    ~~~~~~~~~~

    The page rendering logic for starlit

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from typing import Callable, Tuple
from dataclasses import dataclass
from werkzeug.exceptions import NotFound
from flask import current_app, request, _request_ctx_stack
from starlit.babel import lazy_gettext
from starlit.models.page import Page
from starlit.globals import current_page
from starlit.templating import render_page_template


@dataclass(frozen=True)
class PageHandler:
    view_func: Callable
    methods: Tuple[str]
    module: str


class ContentRendererMixin(object):
    def __init__(self):
        self.contenttype_handlers = {}
        self.before_request(self.set_page_and_response_if_appropriate)
        self.context_processor(self.page_context)
        self.add_contenttype_handler("page", self.default_contenttype_handler)

    def set_page_and_response_if_appropriate(self):
        if isinstance(request.routing_exception, NotFound) and current_page:
            return self.page_view()

    def page_view(self):
        handler = self.get_handler_for(current_page.contenttype)
        if handler is not None:
            _request_ctx_stack.top.module = handler.module
            if request.method not in handler.methods:
                abort(405)
            # TODO: See if the current page have a `serve` method
            rv = handler.view_func()
            if isinstance(rv, dict):
                return render_page_template(context=rv)
            else:
                return rv

    def default_contenttype_handler(self):
        """The default handler for page contenttype"""
        return {}

    def add_contenttype_handler(
        self, contenttype, view_func, methods=("GET",), module=None
    ):
        self.contenttype_handlers[contenttype] = PageHandler(view_func, methods, module)

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
            self.add_contenttype_handler(func, contenttype, methods)
            return func

        return wrapper

    def get_handler_for(self, contenttype):
        return self.contenttype_handlers.get(contenttype)

    def page_context(self):
        pages = (
            Page.query.viewable.filter(Page.is_primary == True)
            .filter(Page.slug_path != current_app.config.get("HOME_SLUG"))
            .all()
        )
        # TODO: refer to the current page using `self`
        return dict(pages=pages, current_page=current_page, page=current_page)
