# -*-coding: utf-8-*-
"""

    [[ project_name ]].models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file contains the project's database models
"""

from sqlalchemy.ext.associationproxy import association_proxy
from oy.models import Page, db
from oy.models.mixins import Ordered
from oy.contrib.media import Image 


class FeaturedContent(db.Model, Ordered):
    page_id = db.Column(db.Integer, db.ForeignKey(Page.id), primary_key=True)
    home_page_id = db.Column(db.Integer, db.ForeignKey("home_page.id"), primary_key=True)
    page = db.relationship(Page, foreign_keys="FeaturedContent.page_id")
    home_page = db.relationship(
        "HomePage",
        foreign_keys="FeaturedContent.home_page_id",
        backref="featured_content",
        cascade="all",
    )


class HomePage(Page):
    __contenttype__ = "home_page"
    id = db.Column(db.Integer, db.ForeignKey(Page.id), primary_key=True)
    intro = db.Column(db.Text)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    image = db.relationship(Image)
    featured_pages = association_proxy("featured_content",
        "page",
        creator=lambda page: FeaturedContent(page=page))
