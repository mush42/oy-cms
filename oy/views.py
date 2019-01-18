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
from werkzeug.exceptions import NotFound
from flask import current_app, render_template, request, _request_ctx_stack
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
        get_templates="process_templates",
        get_context="process_context",
        make_response="process_final_response"
    )

    def __new__(cls, name, bases, d):
        for k, v in d.items():
            if k in cls.func_to_middleware:
                d[k] = cls.wrap_with_middlewares(cls.func_to_middleware[k], v)
        d["middlewares"] = list()
        return type.__new__(cls, name, bases, d)

    @staticmethod
    def wrap_with_middlewares(middleware_funcname, actual_func):
        def wrapper(self, *args, **kwargs):
            rv = actual_func(self, *args, **kwargs)
            for mw in (m() for m in self.handler.middlewares):
                func = getattr(mw, middleware_funcname, None)
                if func is not None:
                    rv = func(rv, handler=self.handler)
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

    def get_templates(self):
        if self.template is not None:
            return self.template
        if self.page.is_home and current_app.config.get("HOME_PAGE_TEMPLATE", ""):
            return current_app.config["HOME_PAGE_TEMPLATE"]
        slug = self.page.slug_path
        templates = ["page", self.page.__contenttype__] + slug.split("/")
        templates.reverse()
        built_tpl_path = lambda prefix: [
            prefix + "{}.html".format(t) for t in templates
        ]
        rv = []
        if getattr(_request_ctx_stack.top, "module", None):
            rv.extend(built_tpl_path(_request_ctx_stack.top.module + "/"))
        return rv + built_tpl_path(current_app.config["PAGE_TEMPLATES_FOLDER"] + "/")

    def get_context(self):
        return self.context

    def render(self, extra_context=None):
        context = self.get_context()
        context.update(**extra_context)
        return render_template(self.get_templates(), **context)

    def serve(self):
        """Subclasses should implement this method."""
        raise NotImplementedError

    def make_response(self):
        """Packages the return type of :meth: `serve` into a response"""
        rv = self.serve()
        if type(rv) is dict:
            return self.render(extra_context=rv)
        return current_app.make_response(rv)


@dataclass(frozen=True)
class PageHandler:
    view: Union[Callable, ContentView]
    methods: Tuple[str]
    module: str
    view_kwargs: dict = field(default_factory=dict)
    middlewares: list = field(default_factory=list)


class ContentViewProcessorMixin(object):
    """A mixin that knows how to serve content."""
    def __init__(self):
        self.contenttype_handlers = {}
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
        if handler is not None:
            _request_ctx_stack.top.module = handler.module
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
                for mw in view.middlewares:
                    rv = mw(rv)
                return current_app.make_response(rv)
            else:
                raise TypeError(
                    f"Unrecognized view handler {view} for contenttype {current_page.contenttype}"
                )

    def add_contenttype_handler(self, contenttype, view, methods=("GET",), module=None):
        self.contenttype_handlers[contenttype] = PageHandler(view, methods, module)

    def contenttype_handler(self, contenttype, methods):
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
        """

        def wrapper(func_or_class):
            if not hasattr(func_or_class, "middlewares"):
                func_or_class.middlewares = []
            self.add_contenttype_handler(func_or_class, contenttype, methods)
            return func

        return wrapper

    def get_handler_for(self, contenttype):
        return self.contenttype_handlers.get(contenttype)

    def apply_middleware(self, contenttype="*", middleware=None):
        if middleware is None:
            raise ValueError("'apply_middleware' invalid argument: 'middleware=None'")
        if contenttype == "*":
            handlers = (c for c in self.contenttype_handlers.values())
        elif contenttype in self.contenttype_handlers:
            handlers = (self.contenttype_handlers[contenttype],)
        else:
            raise ValueError(f"{contenttype} is not a name of a content type handler")
        for hnd in handlers:
            hnd.middlewares.append(middleware)

    def page_context(self):
        pages = Page.query.viewable.roots.ordered.all()
        return {"pages": pages, "current_page": current_page, "page": current_page}
