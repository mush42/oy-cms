from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app
from starlit.boot.exts.sqla import db
from .displayable import Displayable, DisplayableQuery

class PageQuery(DisplayableQuery):
    @property
    def viewable(self):
        return self.published.filter_by(must_show_in_menu=True)

class AbstractPage(Displayable):
    __abstract__ = True
    __metadescription_column__ = 'content'
    query_class = PageQuery
    slug_path = db.Column(db.Unicode(255), unique=True, index=True)
    
    @declared_attr
    def contenttype(cls):
        return db.Column(db.String(50))

    @declared_attr
    def must_show_in_menu(cls):
        return db.Column(
            db.Boolean,
            default=True,
            info=dict(
                label='Show in menu',
                description='Show this page in the navigation menus.'
            )
        )

    @declared_attr
    def parent_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey(cls.id),
            info=dict(
                label='Parent'
            )
        )
    
    @declared_attr
    def children(cls):
        return db.relationship(cls, info=dict(label='Children', description=''))
    
    @declared_attr
    def parent(cls):
        return db.relationship(cls,
            remote_side=cls.id,
            info=dict(
                label='Parent Page',
                description='Parent page'
            )
        )

    @declared_attr
    def content(cls):
        return db.Column(db.UnicodeText, nullable=False,
            info=dict(
                label='Content',
                description='Page content',
                markup=True,
                markup_type='html'
            )
        )

    @declared_attr
    def __mapper_args__(cls):
        return {
            'polymorphic_identity': cls.__contenttype__,
            'polymorphic_on': cls.contenttype
        }

    @property
    def url(self):
        return '/{}/'.format(self.slug_path)

    @hybrid_property
    def is_home(self):
        return self.slug == current_app.config['HOME_SLUG']

    @hybrid_property
    def is_primary(self):
        return self.parent_id == None

    def change_slug_path(self, parent):
        if parent is not None:
            self.slug_path = "%s/%s" %(parent.slug_path, self.slug)
        else:
            self.slug_path = self.slug
        if not self.children:
            return
        for c in self.children:
            c.change_slug_path(parent=self)

    def before_commit(self, session, is_modified):
        session.flush()
        self.change_slug_path(self.parent)

    def __str__(self):
        return self.title
    
    def __repr__(self):
        return "{0}(title='{1}')".format(self.__class__.__name__, self.title)
