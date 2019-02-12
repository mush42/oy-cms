# -*- coding: utf-8 -*-
"""	
    oy.views
    ~~~~~~~~~~

    Implements view logic for oy content.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from typing import Callable, Tuple, Union
from functools import update_wrapper
from dataclasses import dataclass, field
from inspect import signature
from werkzeug.exceptions import NotFound
from flask import _app_ctx_stack, current_app, render_template, request
from oy.babel import lazy_gettext
from oy.models.page import Page
from oy.globals import current_page
from oy.helpers import page_url


class ContentViewType(type):
    """Metaclass for :class:`ContentView` that wrapps selected functions with
    another function that applies all  middlewares.
    """

    func_to_middleware = dict(
        render="process_render",
        serve="process_response",
        get_page="process_page",
        get_template="process_template",
        get_context="process_context",
        make_response="process_final_response",
    )

    def __new__(cls, name, bases, d):
        wrappable = ((k, v) for k, v in d.items() if k in cls.func_to_middleware)
        for funcname, func in wrappable:
            d[funcname] = cls.wrap_with_middlewares(
                cls.func_to_middleware[funcname], func
            )
        return type.__new__(cls, name, bases, d)

    @staticmethod
    def wrap_with_middlewares(middleware_funcname, actual_func):
        def wrapper(self, *args, **kwargs):
            rv = actual_func(self, *args, **kwargs)
            for mw in self.handler.middlewares[middleware_funcname]:
                middleare = mw()
                func = getattr(middleare, middleware_funcname)
                rv = func(rv)
            return rv

        return update_wrapper(wrapper, actual_func)


class ContentView(metaclass=ContentViewType):
    """Builds the final response for the requested content.
    It also applies middlewares.
    """

    def __init__(self, handler, template=None, context=None):
        self.handler = handler
        self.template = template
        self.context = context or {}
        self.page = self.get_page()

    def get_page(self):
        return current_page._get_current_object()

    def get_template(self):
        if self.template is not None:
            return self.template
        slug = self.page.url
        templates = [self.page.contenttype, "page"]
        [templates.insert(0, sl) for sl in slug.split("/")]
        built_tpl_path = lambda prefix: [f"{prefix}/{t}.html" for t in templates]
        rv = built_tpl_path(self.page.contenttype)
        return rv

    def get_context(self):
        return self.context

    def render(self, **extractx):
        context = self.get_context()
        context.update(extractx)
        return render_template(self.get_template(), **context)

    def serve(self):
        """Subclasses can override this method."""
        return self.render()

    def make_response(self):
        """Packages the return type of :meth: `serve` into a response"""
        rv = self.serve()
        if type(rv) is dict:
            return current_app.make_response(self.render(**rv))
        return current_app.make_response(rv)


@dataclass(frozen=True)
class PageHandler:
    view: Union[Callable, ContentView]
    methods: Tuple[str]
    view_kwargs: dict = None
    middlewares: Union[dict, list] = None

    def __post_init__(self):
        if self.view_kwargs is None:
            object.__setattr__(self, "view_kwargs", {})
        if type(self.view) is ContentViewType:
            object.__setattr__(self, "middlewares", {})
            for fname in ContentViewType.func_to_middleware.values():
                self.middlewares[fname] = []
        else:
            object.__setattr__(self, "middlewares", [])

    def _add_func_middleware(self, middleware):
        self.middlewares.append(middleware)

    def _add_class_middleware(self, middleware):
        sortfuncs = self.middlewares.keys()
        mwk = (sf for sf in sortfuncs if hasattr(middleware, sf))
        for k in mwk:
            self.middlewares[k].append(middleware)

    def add_middleware(self, middleware):
        if type(self.view) is ContentViewType:
            self._add_class_middleware(middleware)
        else:
            self._add_func_middleware(middleware)


class ContentViewProcessorMixin:
    """A mixin that make flask apps cabable of serving oy content (pages)."""

    def __init__(self):
        self.contenttype_handlers = {}
        self.before_page_request_funcs = []
        self.context_processor(self.page_context)

    def preprocess_request(self):
        """Override the :func: `Flask.preprocess_request` to return page responses."""
        rv = super().preprocess_request()
        if rv is not None:
            return rv
        if isinstance(request.routing_exception, NotFound) and current_page:
            return self.page_view()

    def page_view(self):
        handler = self.get_handler_for(current_page.contenttype)
        for func in self.before_page_request_funcs:
            rv = func()
            if rv:
                return current_app.make_response(rv)
        if handler is not None:
            _app_ctx_stack.top.handler = handler
            if request.method not in handler.methods:
                abort(405)
            view = handler.view
            if type(view) is ContentViewType:
                return view(handler=handler).make_response()
            elif callable(view):
                rv = view(**handler.view_kwargs)
                for middleware in handler.middlewares:
                    rv = middleware(rv)
                return current_app.make_response(rv)
            else:
                raise TypeError(
                    f"Unrecognized view handler {view} for contenttype {current_page.contenttype}"
                )

    def add_contenttype_handler(
        self, contenttype, view, methods=("GET",), view_kwargs=None
    ):
        if type(contenttype) is not str:
            contenttype = contenttype.__contenttype__
        self.contenttype_handlers[contenttype] = PageHandler(view, methods, view_kwargs)

    def contenttype_handler(self, contenttype, methods=("GET",), view_kwargs=None):
        """A decorator to add custom contenttype handlers to be
        registered with the application

        .. Note::
            This decorator could be used to decorate
            either a function or a subclass of :class: `ContentView`
            
            The return value of view callables is treated as follows:
            - if it is a dictionary, the content of that dictionary will
               be added to the context
             - otherwise it will be passed to the `current_app.make_response` function.

        :param contenttype: a subclass of `Page` or a string that identify a certain page class
        :param methods: a list of HTTP methods that are accepted by this handler
        :param view_kwargs: a dict of keyword arguments used to initialize the view
        """

        def wrapper(func_or_class):
            self.add_contenttype_handler(
                contenttype, func_or_class, methods, view_kwargs
            )
            return func_or_class

        return wrapper

    def get_handler_for(self, contenttype):
        return self.contenttype_handlers.get(contenttype)

    def before_page_request(self, func):
        self.before_page_request_funcs.append(func)
        return func

    def apply_middleware(self, contenttype, middleware):
        if contenttype == "*":
            handlers = self.contenttype_handlers.values()
        elif contenttype in self.contenttype_handlers:
            handlers = (self.contenttype_handlers[contenttype],)
        else:
            raise ValueError(f"{contenttype} is not a name of a content type handler")
        for handler in handlers:
            handler.add_middleware(middleware)

    def page_context(self):
        pages = Page.query.menu_pages.all()
        return {"pages": pages, "current_page": current_page, "page": current_page, "page_url": page_url}
