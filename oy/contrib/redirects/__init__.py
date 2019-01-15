# -*- coding: utf-8 -*-
"""
    oy.contrib.redirects
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    User defined redirects for oy-cms.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from flask import request, redirect as flask_redirect
from oy.contrib.extbase import OyExtBase
from .models import Redirect as RedirectModel
from .admin import register_admin


class Redirects(OyExtBase):
    """Extenssion entry point for oy redirects."""

    module_args = dict(
        name="oy.contrib.redirects",
        import_name="oy.contrib.redirects",
    )

    def init_app(self, app):
        app.before_request_funcs.setdefault(None, []).insert(0, self.redirects_middleware)

    def redirects_middleware(self):
        from_url = RedirectModel.normalize_url(request.url)
        redirect = RedirectModel.query.filter_by(from_url=from_url).one_or_none()
        if redirect is not None:
            status = 301 if redirect.permanent else 307
            return flask_redirect(redirect.link, code=status)
