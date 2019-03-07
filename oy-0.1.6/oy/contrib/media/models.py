# -*- coding: utf-8 -*-
"""
    oy.contrib.media.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides sqlalchemy models for images and documents.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.orm import synonym
from flask import current_app, url_for
from oy.babel import lazy_gettext
from oy.models import db
from .mixins import GenericMedia
from .utils import uploaded_image


class Image(db.Model, GenericMedia):
    id = db.Column(db.Integer, primary_key=True)

    # Nicer aliases for template designers
    file = synonym("uploaded_file")
    alt = synonym("title")
    caption = synonym("description")

    # Uploaded file arguments
    __allowed_file_types__ = ("raster-image",)
    IMG_SIZES = dict(xs=(64, 64), sm=(128, 128), md=(320, 320), lg=(512, 512))
    __depot_args__ = {
        "upload_storage": "image_storage",
        "upload_type": uploaded_image(thumbnail_sizes=IMG_SIZES),
    }

    @property
    def url(self):
        if "media" in current_app.blueprints:
            return url_for("media.images", file_id=self.file_id)


class Document(db.Model, GenericMedia):
    id = db.Column(db.Integer, primary_key=True)
    file = synonym("uploaded_file")

    __allowed_file_types__ = ("document",)
    __depot_args__ = {"upload_storage": "document_storage"}

    @property
    def url(self):
        if "media" in current_app.blueprints:
            return url_for("media.documents", file_id=self.file_id)
