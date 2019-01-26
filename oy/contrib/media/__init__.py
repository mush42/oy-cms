# -*- coding: utf-8 -*-
"""
    oy.contrib.media
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Adds the ability to manage files and documents.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from depot.manager import DepotManager
from oy.contrib.extbase import OyExtBase
from .models import Image, Document
from .admin import register_admin


class Media(OyExtBase):
    """Extenssion entry point for oy media."""

    module_args = dict(
        name="oy.contrib.media",
        import_name="oy.contrib.media",
        static_folder="static",
        template_folder="templates",
    )

    def init_app(self, app):
        storage_conf = app.config.get("DEPOT_STORAGES", None)
        if storage_conf is None:
            raise LookupError(
                "Couldn't find depot storage configuration in app config."
            )
        elif "media_storage" not in storage_conf:
            raise LookupError("The media storage is not configured.")
        for name, args in storage_conf.items():
            DepotManager.configure(name, args)
        for stn in ("image_storage", "document_storage"):
            if DepotManager.get(stn) is None:
                DepotManager.alias(stn, "media_storage")
