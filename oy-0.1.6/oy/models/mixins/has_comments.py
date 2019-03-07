# -*- coding: utf-8 -*-
"""	
    oy.models.mixins.has_comments
    ~~~~~~~~~~

    Provides a mixin classe for comments.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from flask import request
from validators import email
from oy.boot.sqla import db
from oy.helpers import _prepare_association_table
from .misc import SelfRelated
from .time_stampped import TimeStampped


class CommentMixin(SelfRelated):
    author_name = db.Column(db.String(255), nullable=False)
    author_email = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    remote_addr = db.Column(
        db.String(255), nullable=False, default=lambda: request.remote_addr
    )
    user_agent = db.Column(
        db.String(255), nullable=False, default=lambda: request.user_agent
    )

    def __init__(self, author_name, author_email, body):
        self.author_name = author_name
        self.body = body
        if email(author_email):
            self.author_email = author_email
        else:
            raise ValueError(f"{author_email} is not a valid email address.")


class HasComments:
    """Provides a generic many-to-many relationship
    to a  dynamically generated comments table  using
    the `table-per-related` pattern.
    
    .. admonition::: the dynamically generated table is shared by this model
     class and all it's subclasses.
    """

    @declared_attr
    def comments(cls):
        if not hasattr(cls, "Comment"):
            comment_attrs = {"id": db.Column(db.Integer, primary_key=True)}
            cls.Comment = type(
                f"{cls.__name__}Comment", (CommentMixin, db.Model), comment_attrs
            )
            # The many-to-many association table
            cls.__comments_association_table__ = _prepare_association_table(
                table_name=f"{cls.__tablename__}s_comments",
                remote1=cls.__tablename__,
                remote2=cls.Comment.__tablename__,
            )
        return db.relationship(
            cls.Comment, secondary=cls.__comments_association_table__, backref="objects"
        )
