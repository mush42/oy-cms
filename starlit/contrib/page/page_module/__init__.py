# -*- coding: utf-8 -*-
"""
    starlit.contrib.page
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides page  templates and static files
    as well as page editable settings.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from flask import current_app
from starlit.wrappers import StarlitModule
from starlit.babel import lazy_gettext
from ..globals import current_page, parent_page_class
from .admin import register_admin


page_module = StarlitModule(
    'starlit.contrib.page.page_module',
    __name__,
    template_folder="templates",
    viewable_name=lazy_gettext("Page")
)


@page_module.app_context_processor
def enject_pages():
    pages = parent_page_class.query.viewable.filter(
        parent_page_class.is_primary==True).filter(
        parent_page_class.slug_path!=current_app.config.get('HOME_SLUG')
    ).all()
    return dict(
        pages=pages,
        current_page=current_page,
        page=current_page
    )
