# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.misc
    ~~~~~~~~~~

    Provides complementary mixin classes

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import observes
from oy.boot.sqla import db
from oy.helpers import get_owning_table
from ._sqlaevent import SQLAEvent


class SelfRelated(object):
    """A class that have one-to-many relationship with itself."""

    __allowed_child_types__ = ()
    __allowed_parent_types__ = ()
    __children_ordering_column__ = 'id'

    @declared_attr
    def parent_id(cls):
        return db.Column(db.Integer, db.ForeignKey(cls.id), info=dict(label="Parent"))

    @declared_attr
    def children(cls):
        return db.relationship(
            cls,
            lazy="dynamic",
            join_depth=2,
            cascade="all, delete-orphan",
            order_by=f"{cls.__name__}.{cls.__children_ordering_column__}",
            info=dict(label="Children", description=""),
        )

    @declared_attr
    def parent(cls):
        return db.relationship(
            cls,
            remote_side=cls.id,
            info=dict(
                label="Parent Page",
                description="The page under which this page will be added",
            ),
        )

    @hybrid_property
    def is_root(self):
        return self.parent is None

    @is_root.expression
    def is_root(cls):
        return cls.parent_id == None


class Orderable(SQLAEvent):
    """Provide an ordering field."""

    _sort_order = db.Column(db.Integer)
    __children_ordering_column__ = "sort_order"

    @hybrid_property
    def sort_order(self):
        return self._sort_order

    @sort_order.setter
    def sort_order(self, value):
        if not self.id:
            raise RuntimeError("Cannot change order before flushing instance to database")
        ordtbl = get_owning_table(self, "_sort_order")
        whr = [ordtbl.c.id != self.id]
        if "parent" in ordtbl.columns:
            if self.parent:
                whr.append(ordtbl.c.parent_id == self.parent_id)
            else:
                whr.append(ordtbl.c.parent_id == None)
        whrcount = list(whr) + [ordtbl.c._sort_order == value]
        if self.query.filter(db.and_(*whrcount)).count():
            whr.append(ordtbl.c._sort_order >= value)
            up = db.update(ordtbl)\
                .where(db.and_(*whr)).values(_sort_order=ordtbl.c._sort_order + 1)
            db.session.execute(up)
        self._sort_order = value

    def before_flush(self, session, is_modified):
        if not is_modified:
            self._sort_order = None

    def after_flush_postexec(self, session, is_modified):
        if self._sort_order is None:
            self._sort_order = self.id