# -*- coding: utf-8 -*-
"""
    oy.media
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds the ability to manage files such as images and  documents.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from depot.manager import DepotManager
from flask import Blueprint
from .serving import ModelFileServer


class Media:
    """The entry point for oy media."""

    @classmethod
    def configure(cls, app):
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
        if app.config.get("SERVE_MEDIA_FILES"):
            cls._add_serving_routes(app)

    @staticmethod
    def _add_serving_routes(app):
        from oy.models.media import Image, Document
        media_bp = Blueprint("media", __name__, url_prefix=app.config.get("MEDIA_URL_PREFIX", "/media"))
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
