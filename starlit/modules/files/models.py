import os
from collections import namedtuple
from sqlalchemy.ext.declarative import declared_attr
from flask import current_app, url_for
from starlit.boot.exts.sqla import db
from starlit.babel import gettext, lazy_gettext


class FileMixin(object):
    """
    Where to upload this file category
    """
    upload_to = ""

    @declared_attr
    def name(cls):
        return db.Column(db.UnicodeText,
            info=dict(name=lazy_gettext("Upload name"), label="")
        )

    @declared_attr
    def path(cls):
        return db.Column(db.UnicodeText)
    
    @declared_attr
    def description(cls):
        return db.Column(db.UnicodeText,
            info=dict(
                label=lazy_gettext('File description'),
                description=""
            )
        )

    @property
    def url(self):
        path = self.path
        if self.upload_to:
            return url_for("starlit-files.serve_file", filename=self.path, path=self.upload_to)
        return url_for("starlit-files.serve_file", filename=path)
