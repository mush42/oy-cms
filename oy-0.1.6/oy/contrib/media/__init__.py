# -*- coding: utf-8 -*-
"""
    oy.contrib.media
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds the ability to manage files such as images and  documents.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os
from depot.manager import DepotManager
from flask import Blueprint
from oy.contrib.extbase import OyExtBase
from .models import Image, Document
from .admin import register_admin
from .serving import ModelFileServer


class Media(OyExtBase):
    """The entry point for oy media."""

    module_args = {"name": "oy.contrib.media", "import_name": "oy.contrib.media"}

    def init_app(self, app):
        storage_conf = app.config.get("DEPOT_MEDIA_STORAGES", {})
        if not storage_conf:
            raise LookupError(
                """
                Media storage config is required when using the media extension.
                Please add `DEPOT_MEDIA_STORAGES`  to the app config,
        """
            )
        if "media_storage" not in storage_conf:
            raise ValueError(
                "A storage named *media_storage* is required when configuring `DEPOT_STORAGES`."
            )
        for name, opts in storage_conf.items():
            if name not in DepotManager._depots:
                DepotManager.configure(name, opts)
        for storage in ("image_storage", "document_storage"):
            if storage not in DepotManager._depots:
                DepotManager.alias(storage, "media_storage")
        if app.config.get("SERVE_MEDIA_FILES"):
            self._add_serving_routes(app)

    @staticmethod
    def _add_serving_routes(app):
        media_bp = Blueprint(
            "media", __name__, url_prefix=app.config.get("MEDIA_URL_PREFIX", "/media")
        )
        media_bp.add_url_rule(
            "/images/<string:file_id>",
            endpoint="images",
            view_func=ModelFileServer(Image),
        )
        media_bp.add_url_rule(
            "/documents/<string:file_id>",
            endpoint="documents",
            view_func=ModelFileServer(Document),
        )
        app.register_blueprint(media_bp)
