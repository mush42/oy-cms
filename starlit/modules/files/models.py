import os
from collections import namedtuple
from sqlalchemy.ext.declarative import declared_attr
from flask import current_app, url_for
from starlit.boot.exts.sqla import db
from starlit.babel import gettext, lazy_gettext


class ImageMixin(object):
    @declared_attr
    def image_path(cls):
        return db.Column(db.UnicodeText)
    
    @declared_attr
    def image_description(cls):
        return db.Column(db.UnicodeText,
            info=dict(label=lazy_gettext('Image Description'), description=lazy_gettext('If supplying an image please provide a description for the purposes  of ACCESSIBILITY and SEO'))
        )

    @property
    def image(self):
        info = namedtuple('info', 'src description')
        return info(url_for('canella-files.files', filename=self.image_path), self.image_description)