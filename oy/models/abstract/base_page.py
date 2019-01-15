# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.base_page
    ~~~~~~~~~~

    Provides an abstract Page model to be extended

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app
from oy.boot.sqla import db
from oy.helpers import get_owning_table
from ._sqlaevent import SQLAEvent
from .displayable import Displayable


class ScopedUniquelySluggedMixin(object):
    """A slugged which maintains its  uniqueness among its siblings
    within the scope of a specific parent.
    
    The purpose of this mixin is to override just one method in the original slugged mixin.
    """
    def slug_exists(self, session, slug):
        cls = self.__class__
        sel = db.select([cls.slug]).where(db.and_(cls.slug == slug, cls.id != self.id))
        if self.parent_id:
            sel = sel.where(cls.parent_id == self.parent_id)
        return session.execute(sel).fetchone() is not None


class AbstractPage(ScopedUniquelySluggedMixin, Displayable):
    """Extends :class:`Displayable` with special fields"""

    __abstract__ = True
    slug_path = db.Column(
        db.String(5120),
        unique=True,
        index=True
    )

    @declared_attr
    def contenttype(cls):
        return db.Column(db.String(128))

    @declared_attr
    def must_show_in_menu(cls):
        return db.Column(
            db.Boolean,
            default=True,
            info=dict(
                label="Show in menu",
                description="Show this page in the navigation menus.",
            ),
        )

    @declared_attr
    def is_live(cls):
        return db.Column(
            db.Boolean,
            default=True,
            info=dict(
                label="Go Live",
                description="If the page is live, the visitors can view this page, otherwise they will get a page not found error.",
            ),
        )

    @declared_attr
    def parent_id(cls):
        return db.Column(db.Integer, db.ForeignKey(cls.id), info=dict(label="Parent"))

    @declared_attr
    def children(cls):
        return db.relationship(
            cls,
            lazy="joined",
            join_depth=2,
            cascade="all, delete-orphan",
            order_by=f"{cls.__name__}.order",
            info=dict(label="Children", description=""),
        )

    @declared_attr
    def parent(cls):
        return db.relationship(
            cls,
            remote_side=cls.id,
            info=dict(
                label="Parent Page",
                description="The page under which this page will be added"),
        )

    @declared_attr
    def __mapper_args__(cls):
        return dict(
            polymorphic_identity=cls.__contenttype__, polymorphic_on=cls.contenttype
        )

    @db.validates('children')
    def validate_child(self, key, child):
        return child

    @property
    def url(self):
        return "/" + self.slug_path

    @hybrid_property
    def is_home(self):
        return self.slug == current_app.config["HOME_SLUG"]

    @hybrid_property
    def is_root(self):
        return self.parent is None

    @is_root.expression
    def is_root(cls):
        return cls.parent_id == None

    def __str__(self):
        return self.title

    def __repr__(self):
        return "{0}(title='{1}')".format(self.__class__.__name__, self.title)

    def before_flush(self, session, is_modified):
        mods = ('slug', self.__slugcolumn__, 'parent', 'parent_id')
        unmod_cols = db.inspect(self).unmodified
        if is_modified and any(m not in unmod_cols for m in mods):
            self.slug_path = None
        elif not is_modified:
            self.slug_path == None

    def create_or_update_slug_path(self, parent):
        if parent is not None:
            self.slug_path = f"{parent.slug_path}/{self.slug}"
        else:
            self.slug_path = self.slug
        if self.children:
            for child in self.children:
                child.create_or_update_slug_path(parent=self)

    def after_flush_postexec(self, session, is_modified):
        if self.slug_path is None:
            self.create_or_update_slug_path(parent=self.parent)
