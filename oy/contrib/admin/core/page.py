from flask import url_for
from oy.boot.sqla import db
from oy.babel import gettext, lazy_gettext
from oy.models.page import Page
from oy.contrib.admin.core import DisplayableAdmin
from oy.contrib.admin.wtf import TinymceTextAreaField


class PageAdmin(DisplayableAdmin):
    form_rules = [
        (4, "content"),
        (5, "parent"),
        (6, "is_live"),
        (7, "must_show_in_menu"),
    ]
    form_excluded_columns = ["children", "contenttype", "slug_path"]
    column_list = [(1, "parent")]
    form_overrides = {"content": TinymceTextAreaField}

    def edit_form(self, obj):
        return self.modify_edit_form(super(PageAdmin, self).edit_form(obj), page=obj)

    def modify_edit_form(self, form, page):
        form.parent.query_factory = Page.query.filter(Page.id != page.id).all
        return form

    def get_preview_url(instance):
        return f"/{instance.slug_path}/"


def register_page_admin(app, admin):
    admin.add_view(
        PageAdmin(
            Page,
            db.session,
            name=lazy_gettext("Pages"),
            menu_icon_type="fa",
            menu_icon_value="fa-book",
        )
    )