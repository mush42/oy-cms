# -*-coding: utf-8-*-
"""

    [[ project_name ]].home_page.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file contains admin views definition.
"""

from flask_admin.model.form import InlineFormAdmin
from oy.models import Page, db
from oy.contrib.admin import PageAdmin
from oy.contrib.admin.fields import CkeditorTextAreaField
from oy.contrib.media.fields import MediaSelectorField
from oy.contrib.media import Image
from oy.babel import lazy_gettext
from .models import HomePage, FeaturedContent


class InlineFeaturedContentForm(InlineFormAdmin):
    form_columns = ["page", "page_id", "home_page_id"]
    form_label = 'Featured Pages'

    def __init__(self):
        return super(InlineFeaturedContentForm, self).__init__(FeaturedContent)

    def postprocess_form(self, form_class):
        form_class.page.query_factory = lambda: Page.query.filter(
            Page.type != HomePage.__contenttype__
        )
        return form_class


class HomePageAdmin(PageAdmin):
    form_columns = PageAdmin.form_columns + ["image_id",]
    form_columns.insert(4, "intro")
    form_overrides = {"intro": CkeditorTextAreaField, "image_id": MediaSelectorField}
    form_args = {"image_id": {"model": Image, "label": lazy_gettext("Header image")}}
    inline_models = (InlineFeaturedContentForm(),)
        

def register_admin(app, admin):
    admin.add_view(
        HomePageAdmin(
            HomePage,
            db.session,
            name="home page",
            verbose_name="home pages",
            menu_icon_type="fa",
            menu_icon_value="fa-home",
            menu_order=1000,
        )
    )
