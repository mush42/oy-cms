# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.misc
    ~~~~~~~~~~

    Provides complementary mixin classes

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from oy.boot.sqla import db
from oy.helpers import get_owning_table
from ._sqlaevent import SQLAEvent


class SelfRelated:
    """A class that have many-to-many  relationship with itself.
    This class implements the `Adjacency List` patterns of managing hierarchical data.
    ."""

    __allowed_child_types__ = ()
    __allowed_parent_types__ = ()
    __children_ordering_column__ = "id"

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
        return self.parent_id == None


class Ordered(SQLAEvent):
    """Provide an ordering field."""

    sort_order = db.Column(db.Integer)
    __children_ordering_column__ = "sort_order"

    def after_flush_postexec(self, session, is_modified):
        if self.sort_order is None:
            self.sort_order = db.inspect(self).mapper.primary_key[0]
