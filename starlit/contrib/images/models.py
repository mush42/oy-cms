import os
from collections import namedtuple
from sqlalchemy.ext.declarative import declared_attr
from flask import current_app, url_for
from starlit.boot.exts.sqla import db
from starlit.modeuls.files.models import FileMixin
from starlit.babel import gettext, lazy_gettext
from .images import resized_img_src


class Image(FileMixin):
    info = namedtuple('img_info', 'url description')

    @declared_attr
    def alt_text(cls):
        return db.Column(db.UnicodeText,
            info=dict(
                label=lazy_gettext('Alternative Text'),
                description=lazy_gettext('Provide an alternative description for the purposes  of ACCESSIBILITY and SEO')
            )
        )

    @property
    def image(self, **kwargs):
        img_url = resized_img_src(self.image_path, **kwargs)
        return self.info(img_url, self.alt_text)
