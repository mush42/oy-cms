# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.base_page
    ~~~~~~~~~~

    Provides an abstract Page model.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from itertools import chain
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_mptt.mixins import BaseNestedSets
from oy.boot.sqla import db
from oy.models.mixins import ScopedUniquelySlugged, NodeSpec
from .displayable import Displayable


class AbstractPage(NodeSpec, Displayable, BaseNestedSets, ScopedUniquelySlugged):
    """Extends :class:`Displayable` with special fields"""

    __abstract__ = True

    url_path = db.Column(db.String(1024), unique=True, nullable=True, index=True)

    @hybrid_property
    def url(self):
        return self.url_path

    @staticmethod
    def construct_url_path(page):
        slugs = [p.slug for p in page.path_to_root(order=db.asc)]
        return "/".join(slugs)

    def before_commit(self, session, is_modified):
        session.flush()
        state = db.inspect(self)
        tbl = state.mapper.primary_base_mapper.tables[0]
        rps = [self.slug]
        parent = self.parent
        while parent is not None:
            rps.append(parent.slug)
            parent = parent.parent
        rps.reverse()
        new_url_path = "/".join(rps)
        up = db.update(tbl).where(tbl.c.id == self.id).values(url_path=new_url_path)
        session.execute(up)
        session.refresh(self)
        with session.no_autoflush:
            for child in self.children:
                AbstractPage.before_commit(child, session, True)

    def __repr__(self):
        return f'<{self.__class__.__name__}(title="{self.title}")>'
