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
from flask import current_app, render_template, request
from oy.babel import lazy_gettext
from oy.models.page import Page
from oy.globals import current_page


class ContentViewType(type):
    """Metaclass for :class:`ContentView` that wrapps selected functions with
    another function that applies all  middlewares.
    """

    func_to_middleware = dict(
        render="process_render",
        serve="process_response",
        get_template="process_template",
        get_context="process_context",
        make_response="process_final_response"
    )

    def __new__(cls, name, bases, d):
        wrappable = ((k, v) for k, v in d.items() if k in cls.func_to_middleware)
        for funcname, func in wrappable:
            d[funcname] = cls.wrap_with_middlewares(cls.func_to_middleware[funcname], func)
        return type.__new__(cls, name, bases, d)

    @staticmethod
    def wrap_with_middlewares(middleware_funcname, actual_func):

        def wrapper(self, *args, **kwargs):
            rv = actual_func(self, *args, **kwargs)
            for mw in self.handler.middlewares[middleware_funcname]:
                func = getattr(mw, middleware_funcname)
                rv = func(rv)
            return rv

        return update_wrapper(wrapper, actual_func)


class ContentView(metaclass=ContentViewType):
    """A configurational object that contains content response data
    it also applies middlewares.
    """

    def __init__(self, handler, template=None, context=None):
        self.handler = handler
        self.template = template
        self.context = context or {}
        self.page = current_page._get_current_object()

    def get_template(self):
        if self.template is not None:
            return self.template
        if self.page.is_home and current_app.config.get("HOME_PAGE_TEMPLATE", ""):
            return current_app.config["HOME_PAGE_TEMPLATE"]
        slug = self.page.slug_path
        templates =  [self.page.contenttype, "page"]
        [templates.insert(0, sl) for sl in slug.split("/")]
        built_tpl_path = lambda prefix: [
            f"{prefix}/{t}.html" for t in templates
        ]
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
    view_kwargs: dict = field(default_factory=dict)
    middlewares: dict = field(default_factory=dict)


    def __post_init__(self):
        for fname in ContentViewType.func_to_middleware.values():
            self.middlewares[fname] = []


class ContentViewProcessorMixin:
    """A mixin that knows how to serve content."""

    def __init__(self):
        self.contenttype_handlers = {}
        self.before_page_request_funcs  = []
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
            rv = func(handler)
            if rv:
                return current_app.make_response(rv)
        if handler is not None:
            if request.method not in handler.methods:
                abort(405)
            view = handler.view
            if type(view) is ContentViewType:
                return view(handler=handler).make_response()
            elif type(view) is ContentView:
                view.handler = handler
                return view.make_response()
            elif callable(view):
                rv = view(**handler.view_kwargs)
                for mw in handler.middlewares:
                    rv = mw(rv)
                return current_app.make_response(rv)
            else:
                raise TypeError(
                    f"Unrecognized view handler {view} for contenttype {current_page.contenttype}"
                )

    def add_contenttype_handler(self, contenttype, view, methods=("GET",), view_kwargs=None):
        self.contenttype_handlers[contenttype] = PageHandler(view, methods, view_kwargs)

    def contenttype_handler(self, contenttype, methods=("GET",), view_kwargs=None):
        """A decorator to add custom contenttype handlers to be
        registered with the application

        .. Note::
            This decorator accepts either a function or a subclass of :class: `ContentView`
            
            The return value of view callables is treated as follows:
            - if it is a dictionary, the content of that dictionary will
               be added to the context
             - if it is anything else, it will be returned as is

        :param contenttype: a string that identify a certain page class
        :param methods: a list of HTTP methods that are accepted by this handler
        :param view_kwargs: a dict of keyword arguments used to initialize the view
        """

        def wrapper(func_or_class):
            self.add_contenttype_handler(contenttype, func_or_class, methods, view_kwargs)
            return func_or_class

        return wrapper

    def get_handler_for(self, contenttype):
        return self.contenttype_handlers.get(contenttype)

    def before_page_request(self, func):
        self.before_page_request_funcs.append(func)
        return func

    def apply_middleware(self, contenttype="*", middleware=None):
        if middleware is None:
            raise ValueError("'apply_middleware' invalid argument: 'middleware=None'")
        if contenttype == "*":
            handlers = (c for c in self.contenttype_handlers.values())
        elif contenttype in self.contenttype_handlers:
            handlers = (self.contenttype_handlers[contenttype],)
        else:
            raise ValueError(f"{contenttype} is not a name of a content type handler")
        sig = signature(middleware)
        if len(sig.parameters) == 1 and "handler" in sig.parameters:
            initmw = True
        elif not sig.parameters:
            initmw = False
        else:
            raise TypeError("""
                Cannot apply middleware.
                
                The middleware' s__init__ method should either
                accept one argument called `handler` .
                or no argument at all.
            """)
        for hnd in handlers:
            initialized_middleware = middleware(hnd) if initmw else middleware()
            if initmw:
                initialized_middleware.handler = hnd
            sortfuncs = hnd.middlewares.keys()
            mwk = (sf for sf in sortfuncs if hasattr(middleware, sf))
            for k in mwk:
                hnd.middlewares[k].append(initialized_middleware)

    def page_context(self):
        pages = Page.query.viewable.roots.ordered.all()
        return {"pages": pages, "current_page": current_page, "page": current_page}
