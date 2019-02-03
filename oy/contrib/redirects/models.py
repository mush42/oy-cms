# -*- coding: utf-8 -*-
"""
    oy.contrib.redirects.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides sqlalchemy models for redirects.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from urllib.parse import urlparse
from sqlalchemy.orm import validates
from oy.models import Page, db
from oy.models.abstract import SQLAEvent
from oy.babel import lazy_gettext


class Redirect(db.Model, SQLAEvent):
    id = db.Column(db.Integer, primary_key=True)
    from_url = db.Column(
        db.String(1024),
        nullable=False,
        unique=True,
        index=True,
        info=dict(
            label=lazy_gettext("Redirect From"),
            description=lazy_gettext("Old URL to redirect from"),
        ),
    )
    to_url = db.Column(
        db.String(1024),
        info=dict(
            label=lazy_gettext("Redirect to"),
            description=lazy_gettext("Redirect to this URL"),
        ),
    )
    to_page_id = db.Column(db.Integer, db.ForeignKey(Page.id))
    permanent = db.Column(
        db.Boolean,
        default=False,
        info=dict(
            label=lazy_gettext("Permanent Redirect"),
            description=lazy_gettext("Check this to make this a permanent redirect"),
        ),
    )

    to_page = db.relationship(
        Page,
        backref="redirects",
        cascade="all",
        info=dict(
            label=lazy_gettext("Select a *Page* to Redirect to"),
            description=lazy_gettext(""),
        ),
    )

    @validates("to_url")
    def norm_tourl(self, key, to_url):
        if to_url is not None:
            return self.normalize_url(to_url)

    @validates("from_url")
    def norm_fromurl(self, key, from_url):
        return self.normalize_url(from_url)

    @property
    def url(self):
        return self.to_url or self.to_page.url

    @staticmethod
    def normalize_url(url):
        """Taken from wagtail CMS."""
        url = url.strip()
        url_parsed = urlparse(url)
        path = url_parsed[2]
        if not path.startswith("/"):
            path = "/" + path
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]
        # Parameters must be sorted alphabetically
        parameters = url_parsed[3]
        parameters_components = parameters.split(";")
        parameters = ";".join(sorted(parameters_components))
        # Query string components must be sorted alphabetically
        query_string = url_parsed[4]
        query_string_components = query_string.split("&")
        query_string = "&".join(sorted(query_string_components))
        if parameters:
            path = path + ";" + parameters
        # Add query string to path
        if query_string:
            path = path + "?" + query_string
        return path

    def __repr__(self):
        return f"<Redirect from: {self.from_url}, to={self.url}, permanent: {self.permanent}>"

    def before_flush(self, session, is_modified):
        if self.to_url and any((self.to_page_id, self.to_page)):
            raise ValueError("Cannot set both URL and Page for the same redirect")
        elif not any((self.to_url, self.to_page, self.to_page_id)):
            raise ValueError("You must provide either a URL or a page to redirect to.")
