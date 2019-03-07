# -*- coding: utf-8 -*-
"""	
    oy.models.mixins.classifiable
    ~~~~~~~~~~

    Provides mixin classes for classifying content,
    namely for adding tags and categories.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from oy.boot.sqla import db
from oy.helpers import _prepare_association_table
from .slugged import Titled, Slugged


class ClassifierMixin(Titled, Slugged):
    """Provides basic fields for a tag or a category item."""


class Tagged:
    """Provides a generic many-to-many relationship
    to a  dynamically generated tags table  using
    the `table-per-related` pattern.
    
    .. admonition::: the dynamically generated table is shared by this model
     class and all it's subclasses.
    """

    @declared_attr
    def tags(cls):
        if not hasattr(cls, "Tag"):
            # Create the Tag model
            tag_attrs = {
                "id": db.Column(db.Integer, primary_key=True),
                "objects": db.relationship(
                    cls,
                    secondary=lambda: cls.__tags_association_table__,
                    backref="related_tags",
                ),
            }
            cls.Tag = type(f"{cls.__name__}Tag", (ClassifierMixin, db.Model), tag_attrs)
            # The many-to-many association table
            cls.__tags_association_table__ = _prepare_association_table(
                table_name=f"{cls.__tablename__}s_tags",
                remote1=cls.__tablename__,
                remote2=cls.Tag.__tablename__,
            )
        return association_proxy(
            "related_tags", "title", creator=lambda t: cls.Tag.get_or_create(title=t)
        )


class Categorized:
    """Provides a generic Foreign Key relationship to a 
    dynamically generated category table  using
    the `table-per-related` pattern.

    .. admonition::: the dynamically generated table is shared by this model
     class and all it's subclasses.
    """

    @declared_attr
    def category_id(cls):
        if not hasattr(cls, "Category"):
            category_attrs = {
                "id": db.Column(db.Integer, primary_key=True),
                "objects": db.relationship(cls, backref="category"),
            }
            cls.Category = type(
                f"{cls.__name__}Category", (ClassifierMixin, db.Model), category_attrs
            )
        return db.Column(db.Integer, db.ForeignKey(cls.Category.id))
