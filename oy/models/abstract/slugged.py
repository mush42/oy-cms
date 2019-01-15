# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.slugged
    ~~~~~~~~~~

    Provide a mixin class for slugged content.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app
from oy.boot.sqla import db
from oy.slugging import slugify
from oy.helpers import increment_string, get_owning_table
from ._sqlaevent import SQLAEvent


class Titled(SQLAEvent):
    """Provide a mandatory title field"""

    title = db.Column(
        db.Unicode(512),
        nullable=False,
        info=dict(
            label="Title", description="The title to display in the browser title bar."
        ),
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return "{0}(title={1})".format(self.__class__.__name__, self.title)


class Slugged(SQLAEvent):
    """A slugged mixin class"""

    slug = db.Column(
        db.Unicode(512),
        info=dict(
            label="Slug",
            description="A Slug is that portion of the URL used to identify this content.",
        ),
    )
    __slugcolumn__ = 'title'

    def create_slug(self):
        candidate = getattr(self, self.__slugcolumn__)
        return self.slugify(candidate)

    def slugify(self, string):
        return slugify(string)

    def _ensure_slug_uniqueness(self, session, slug):
        original_slug = slug
        while True:
            if not self.slug_exists(session, slug):
                return slug
            slug = increment_string(slug, sep='-')

    def slug_exists(self, session, slug):
        cls = self.__class__
        sel = db.select([cls.slug]).where(db.and_(cls.slug == slug, cls.id != self.id))
        return session.execute(sel).fetchone() is not None

    def before_flush(self, session, is_modified):
        if is_modified and self.__slugcolumn__ not in db.inspect(self).unmodified:
            self.slug = None

    def after_flush_postexec(self, session, is_modified):
        if self.slug is not None:
            return
        slug = self._ensure_slug_uniqueness(session, self.create_slug())
        slugtbl = get_owning_table(entity=self, colname='slug').name
        txt = db.text(f"UPDATE {slugtbl} SET slug=:slug WHERE {slugtbl}.id = :id_1")\
            .bindparams(slug=slug, id_1=self.id)
        session.execute(txt)

