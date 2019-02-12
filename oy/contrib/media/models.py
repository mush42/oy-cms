# -*- coding: utf-8 -*-
"""
    oy.contrib.media.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides sqlalchemy models for images and documents.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from secrets import token_urlsafe
from sqlalchemy.orm import synonym
from sqlalchemy.ext.declarative import declared_attr
from depot.fields.sqlalchemy import UploadedFileField
from flask import current_app, url_for
from oy.models import db
from oy.models.abstract import Titled, TimeStampped, UserRelated, Tagged
from oy.babel import lazy_gettext
from .filters import FileTypeCheckFilter, WithThumbnailFilter


NUMBYTES = 16


class UploadableMediaMixin(Titled, TimeStampped, UserRelated, Tagged):
    file_id = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: token_urlsafe(NUMBYTES)
    )
    description = db.Column(
        db.Text, nullable=True, info=dict(lable=lazy_gettext("Description"))
    )

    __depot_args__ = {"upload_storage": "media_storage"}

    @declared_attr
    def uploaded_file(cls):
        depot_args = dict(cls.__depot_args__)
        filters = depot_args.pop("filters", [])
        allowed_files = getattr(cls, "__allowed_file_types__", [])
        if allowed_files:
            filters.insert(0, FileTypeCheckFilter(filetypes=allowed_files))
        return db.Column(
            UploadedFileField(filters=filters, **depot_args),
            nullable=False,
            info=dict(label=lazy_gettext("Select a file")),
        )

    def before_insert(self, mapper, connection):
        tbl = mapper.mapped_table
        sel = db.select([tbl.c.id])
        token = token_urlsafe(14)
        while connection.scalar(db.func.count(sel.where(tbl.c.file_id == token))):
            token = token_urlsafe(NUMBYTES)
        self.file_id = token

    @classmethod
    def get_upload_storage(cls):
        return db.inspect(cls).get_property("uploaded_file").columns[0].type._upload_storage


class Image(db.Model, UploadableMediaMixin):
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
        "filters": [
            WithThumbnailFilter(name=name, size=size, format="png")
            for name, size in IMG_SIZES.items()
        ],
    }

    @property
    def url(self):
        if "media" in current_app.blueprints:
            return url_for("media.images", file_id=self.file_id)

    def get_thumbnail_id(self, size):
        """ Returns the thumbnail id with the given size (e.g. 'sm').
        """
        name = f"thumbnail_{size}"
        if name not in self.uploaded_file:
            return
        return self.uploaded_file[name]["id"]


class Document(db.Model, UploadableMediaMixin):
    id = db.Column(db.Integer, primary_key=True)
    file = synonym("uploaded_file")

    __allowed_file_types__ = ("document",)
    __depot_args__ = {"upload_storage": "document_storage"}

    @property
    def url(self):
        if "media" in current_app.blueprints:
            return url_for("media.documents", file_id=self.file_id)
