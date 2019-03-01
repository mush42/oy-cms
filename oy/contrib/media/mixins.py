# -*- coding: utf-8 -*-
"""	
    oy.contrib.media.mixins
    ~~~~~~~~~~

    Provides a mixin classe for uploaded content.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os
from secrets import token_urlsafe
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.datastructures import FileStorage
from depot.fields.sqlalchemy import UploadedFileField
from depot.io.utils import FileIntent
from oy.babel import lazy_gettext
from oy.models import db
from oy.models.mixins import DynamicProp, Titled, TimeStampped, UserRelated, Tagged
from oy.helpers import slugify
from oy.contrib.demo_content.utils import (
    deserialize_instance as original_deserialize_instance,
)
from .utils import FileTypeCheckFilter


# Number of random bytes of the file_id value.
NUMBYTES = 16


class GenericMedia(Titled, TimeStampped, UserRelated, Tagged):
    file_id = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: token_urlsafe(NUMBYTES),
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
        filename, ext = os.path.splitext(self.uploaded_file.filename)
        self.file_id = f"{slugify(filename)}-{token}{ext}"

    @classmethod
    def get_upload_storage(cls):
        return (
            db.inspect(cls)
            .get_property("uploaded_file")
            .columns[0]
            .type._upload_storage
        )

    @staticmethod
    def deserialize_instance(module, model, **attrs):
        """Custom logic for constructing object from json when adding demo data."""
        with db.session.no_autoflush:
            file = open(
                os.path.join(module.root_path, "fixtures", attrs["uploaded_file"]), "rb"
            )
            attrs["uploaded_file"] = file
            obj = original_deserialize_instance(module, model, **attrs)
            file.close()
        return obj


class DynamicPropWithFile(DynamicProp):
    @declared_attr
    def file_value(cls):
        kwargs = getattr(cls, "__file_field_args__", {})
        nullable = kwargs.pop("nullable", True)
        info = kwargs.pop("info", {})
        info["type"] = ((FileIntent, FileStorage), "file")
        return db.Column(UploadedFileField(**kwargs), nullable=nullable, info=info)
