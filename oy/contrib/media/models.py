# -*- coding: utf-8 -*-
"""
    oy.contrib.media.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides sqlalchemy models for images and documents.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.orm import synonym
from sqlalchemy.ext.declarative import declared_attr
from depot.fields.sqlalchemy import UploadedFileField
from depot.fields.filters.thumbnails import WithThumbnailFilter
from oy.models import db
from oy.models.events import SQLAEvent
from oy.models.abstract.slugged import Titled
from oy.models.abstract.publishable import Publishable
from oy.models.abstract.time_stampped import TimeStampped
from oy.models.abstract.user_related import UserRelated
from oy.babel import lazy_gettext


class UploadableMediaMixin(Titled, Publishable, TimeStampped, UserRelated):

    container = db.Column(db.String(255))
    __depot_args__ = {"upload_storage": "media_storage"}

    @declared_attr
    def file(cls):
        depot_args = cls.__depot_args__
        return db.Column(UploadedFileField(**depot_args), nullable=False)


class Image(db.Model, UploadableMediaMixin):
    id = db.Column(db.Integer, primary_key=True)
    image = synonym("file")
    album = synonym("container")
    __depot_args__ = {
        "upload_storage": "image_storage",
        "filters": (WithThumbnailFilter,),
    }


class Document(db.Model, UploadableMediaMixin):
    id = db.Column(db.Integer, primary_key=True)
    document = synonym("file")
    folder = synonym("container")
    __depot_args__ = {"upload_storage": "document_storage"}
