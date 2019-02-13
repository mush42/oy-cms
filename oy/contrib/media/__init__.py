# -*- coding: utf-8 -*-
"""
    oy.contrib.media
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Adds the ability to manage files and documents.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from depot.manager import DepotManager
from flask import Blueprint
from oy.contrib.extbase import OyExtBase
from .models import Image, Document
from .serving import ModelFileServer
from .admin import register_admin


class Media(OyExtBase):
    """Extenssion entry point for oy media."""

    module_args = dict(name="oy.contrib.media", import_name="oy.contrib.media")

    def __init__(
        self, app=None, serve_files=False, media_url_prefix="/media", **module_args
    ):
        self.serve_files = serve_files
        self.media_url_prefix = media_url_prefix
        super().__init__(app, **module_args)

    def init_app(self, app):
        storage_conf = app.config.get("DEPOT_MEDIA_STORAGES", None)
        if storage_conf is None:
            raise LookupError(
                "Couldn't find depot storages configuration in app config."
            )
        if "media_storage" not in storage_conf:
            raise ValueError(
                "A storage named *media_storage* is required when configuring `DEPOT_STORAGES`."
            )
        for name, opts in storage_conf.items():
            DepotManager.configure(name, opts)
        for storage in ("image_storage", "document_storage"):
            if storage not in DepotManager._depots:
                DepotManager.alias(storage, "media_storage")
        # Register the module that will serve admin static files
        app.register_blueprint(
            Blueprint(
                name="oy.contrib.media.admin",
                import_name="oy.contrib.media",
                static_folder="static",
                template_folder="templates",
            )
        )
        if self.serve_files:
            self._add_serving_routes(app)

    def _add_serving_routes(self, app):
        media_bp = Blueprint("media", __name__, url_prefix=self.media_url_prefix)
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
