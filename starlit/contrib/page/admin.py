from flask import url_for
from starlit.boot.sqla import db
from starlit.babel import gettext, lazy_gettext
from starlit.contrib.admin.core import DisplayableAdmin
from starlit.contrib.admin.wtf import TinymceTextAreaField
from .models import Page


class PageAdmin(DisplayableAdmin):
    form_rules = [(4, "content"), (5, "parent"), (6, "is_live"), (7, "must_show_in_menu"),]
    form_excluded_columns = ["children", "contenttype", "slug_path"]
    column_list = [(1, "parent")]
    form_overrides = {
        'content': TinymceTextAreaField
    }

    def edit_form(self, obj):
        return self.modify_edit_form(super(PageAdmin, self).edit_form(obj), page=obj)

    def modify_edit_form(self, form, page):
        form.parent.query_factory = Page.query.filter(Page.id != page.id).all
        return form

    def get_preview_url(instance):
        return instance.slug_path


def register_admin(app, admin):
    admin.add_view(PageAdmin(
        Page,
        db.session,
        name=lazy_gettext('Pages'),
        menu_icon_type='fa',
        menu_icon_value='fa-book'
    ))