from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from flask import current_app
from flask_sqlalchemy import BaseQuery
from flask_security import current_user
from starlit.boot.exts.sqla import db
from starlit.babel import lazy_gettext

from ._sqlaevent import SQLAEvent
from .slugged import Slugged, Titled
from .metadata import Metadata
from .publishable import Publishable


class DisplayableQuery(BaseQuery):
    @property
    def published(self):
        pub = self._joinpoint_zero().columns['publish_date']
        expire = self._joinpoint_zero().columns['expire_date']
        rv = self.filter_by(status='published').filter(pub<=datetime.utcnow())
        if expire is not None:
            rv.filter(expire>=datetime.utcnow())
        return rv

class Displayable(db.Model, Titled, Slugged, Metadata, Publishable):
    """Displayable"""
    __abstract__ = True
    __slugcolumn__ = 'title'
    __keywordscolumn__ = 'title'
    __metatitle_column__ = 'title'
    query_class = DisplayableQuery

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def site_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('site.id'),
            info=dict(label='Site')
            )

    @declared_attr
    def site(cls):
        return db.relationship('Site',
            info=dict(label='Site', description='The site to wich this content will be published')
        )

    @declared_attr
    def user_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('user.id'),
            info=dict(label=lazy_gettext('Author'))
            )

    @declared_attr
    def author(cls):
        return db.relationship('User',
            info=dict(label=lazy_gettext('Author'), description=lazy_gettext(''))
            )

    def set_current_user(self):
        if not self.user_id:
            self.user_id = current_user.id

    def on_init(self):
        self.set_current_user()

    def update(self):
        self.set_current_user()