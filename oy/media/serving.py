# -*- coding: utf-8 -*-
"""
    oy.contrib.media.serving
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the media serve view.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from depot.middleware import FileServeApp
from flask import abort


class ModelFileServer:
    """Serves files from database."""

    def __init__(self, model):
        self.model = model

    def __call__(self, file_id):
        obj = self.model.query.filter_by(file_id=file_id).one_or_none()
        if obj is None:
            abort(404)
        return FileServeApp(storedfile=obj.uploaded_file.file, cache_max_age=0)
