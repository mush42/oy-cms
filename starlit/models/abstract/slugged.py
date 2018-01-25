from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app
from starlit.boot.exts.sqla import db
from starlit.util.slugging import slugify
from ._sqlaevent import SQLAEvent


class Titled(SQLAEvent):
    title = db.Column(
        db.Unicode(255),
        nullable=False,
        info=dict(
            label='Title',
            description='The title to display in the browser title bar.'
        )
    )

    def __str__(self):
        return self.title
    __unicode__ = __str__

    def __repr__(self):
        return '{0}(title={1})'.format(self.__class__.__name__, self.title)


class Slugged(SQLAEvent):
    slug = db.Column(
        db.Unicode(255),
        unique=True,
        index=True,
        info=dict(
            label='Slug',
            description='A Slug is that portion of the URL used to identify this content.'
        )
    )

    def before_flush(self, session, is_modified):
        if not self.slug or self._slug_exists(session, self.slug):
            self._update_slug(session)
        if is_modified and current_app.config['ALLWAYS_UPDATE_SLUGS']:
            state = inspect(self)
            if self.__slugcolumn__ not in state.unmodified:
                self.slug = None
                self.before_flush(session, is_modified=False)

    def _update_slug(self, session):
        populates_from = getattr(self, '__slugcolumn__', None)
        if populates_from is None:
            raise AssertionError(
                "You must specify the column the slug is populated from."
            )
        value = getattr(self, populates_from)
        slug = slugify(value)
        slug = self._ensure_slug_uniqueness(session, slug)
        self.slug = slug

    def _slug_exists(self, session, slug):
        try:
            obj = self.__class__.query.filter_by(slug=slug).one()
            return obj is not self
        except NoResultFound:
            return False

    def _ensure_slug_uniqueness(self, session, slug):
        original_slug = slug
        index = 1
        while True:
            if not self._slug_exists(session, slug):
                return slug
            index += 1
            slug = u'%(slug)s-%(index)s' % {
                'slug': original_slug,
                'index': index
            }
