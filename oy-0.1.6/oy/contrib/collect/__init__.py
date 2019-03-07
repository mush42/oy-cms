# -*- coding: utf-8 -*-
"""
    oy.contrib.collect
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Collect static files to be served in production.
    This code is heavily inspired by the excellent `flask-collect` extension.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.contrib.extbase import OyExtBase
from .cli import collect_static


class CollectStatic(OyExtBase):
    """Extenssion entry point for oy collect."""

    name = "oy.contrib.collect"

    def init_app(self, app):
        app.config.setdefault(
            "COLLECT_STORAGE", "oy.contrib.collect.storages:LocalFileSystemStorage"
        )
        app.cli.add_command(collect_static)
