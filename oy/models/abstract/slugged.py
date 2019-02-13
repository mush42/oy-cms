# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.slugged
    ~~~~~~~~~~

    Provide  mixin classes for slugged content.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app
from oy.boot.sqla import db
from slugify import slugify
from oy.helpers import increment_string, get_owning_table
from ._sqlaevent import SQLAEvent


class Titled(SQLAEvent):
    """Provide a mandatory title field"""

    title = db.Column(
        db.Unicode(512),
        nullable=False,
        info=dict(label="Title", description="The title to display for the end user."),
    )

    def __str__(self):
        return self.title


class Slugged(SQLAEvent):
    """A slugged mixin class"""

    __slugcolumn__ = "title"

    @declared_attr
    def slug(cls):
        return db.Column(
            db.Unicode(255),
            info=dict(
                label="Slug",
                description="A Slug is that portion of the URL used to identify this content.",
            ),
        )

    def redundant_slug_exists(self, slug):
        cls = self.__class__
        q = db.session.query(cls).filter(cls.id != self.id).filter(cls.slug == slug)
        return q.count()

    def make_unique(self, slug):
        while True:
            if not self.redundant_slug_exists(slug):
                return slug
            slug = self.generate_unique_slug(slug)

    def before_flush(self, session, is_modified):
        if not self.slug:
            self.slug = self.slugify(getattr(self, self.__slugcolumn__))

    def after_flush(self, session, is_modified):
        slug = self.make_unique(self.slug)
        if slug != self.slug:
            slugtbl = get_owning_table(entity=self, colname="slug").name
            txt = db.text(
                f"UPDATE {slugtbl} SET slug=:slug WHERE {slugtbl}.id = :id_1"
            ).bindparams(slug=slug, id_1=self.id)
            session.execute(txt)

    @staticmethod
    def slugify(string):
        return slugify(string)

    @staticmethod
    def generate_unique_slug(slug):
        return increment_string(slug, sep="-")


class ScopedUniquelySlugged(Slugged):
    """A slugged which maintains its  uniqueness among its siblings
    within the scope of a specific parent.
    """

    def redundant_slug_exists(self, slug):
        cls = self.__class__
        q = db.session.query(cls).filter(cls.id != self.id).filter(cls.slug == slug)
        if self.parent:
            q = q.filter(cls.parent == self.parent)
        else:
            q = q.filter(cls.parent == None)
        return q.count()
