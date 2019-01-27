# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.tagable
    ~~~~~~~~~~

    Provides a mixin classe for tagging content.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from oy.boot.sqla import db
from .slugged import Titled, Slugged


def _prepare_association_table(table_name, remote1, remote2):
    return db.Table(table_name, db.metadata,
        db.Column(f"{remote1}_id", db.Integer, db.ForeignKey(f"{remote1}.id")),
        db.Column(f"{remote2}_id", db.Integer, db.ForeignKey(f"{remote2}.id"))
    )


class TagMixin(Titled, Slugged):
    """Provides basic fields for the dynamically  generated `Tag` table."""


class Tagable:
    """Provides a generic many-to-many `tags` relationship with another
    model using the `table-per-related` pattern.
    """

    @declared_attr
    def tags(cls):
        if not hasattr(cls, "Tag"):
            # Create the Tag model
            tag_attrs =                 {
                "id": db.Column(db.Integer, primary_key=True),
                "objects": db.relationship(
                    cls, secondary=lambda: cls.__tags_association_table__, backref="related_tags"
                )
            }
            cls.Tag = type(
                f"{cls.__name__}Tag",
                (TagMixin, db.Model,),
                tag_attrs
            )
            # The many-to-many association table
            cls.__tags_association_table__ = _prepare_association_table(
                table_name=f"{cls.__tablename__}s_tags",
                remote1=cls.__tablename__,
                remote2=cls.Tag.__tablename__
            )
        return association_proxy("related_tags", "title", creator=lambda t: cls.Tag.get_or_create(title=t))
