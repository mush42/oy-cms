# -*- coding: utf-8 -*-
"""
    starlit.contrib.page
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides page  templates and static files
    as well as page editable settings.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from starlit.wrappers import StarlitModule


page_resource_module = StarlitModule(
    'starlit.contrib.page',
    __name__,
    static_folder="static",
    template_folder="templates",
    viewable_name=lazy_gettext("Page")
)


@page_resource_module.app_context_processor
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
