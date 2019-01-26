# -*-coding: utf-8-*-
"""

    [[ project_name ]].models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file contains the project's database models
"""

from oy.models import Page, db


class HomePage(Page):
    __contenttype__ = "home_page"
    id = db.Column(db.Integer, db.ForeignKey(Page.id), primary_key=True)

