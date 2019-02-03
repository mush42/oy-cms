from flask import url_for
from oy.boot.sqla import db
from oy.babel import gettext, lazy_gettext
from oy.models.page import Page
from .displayable_admin import DisplayableAdmin, DISPLAYABEL_DEFAULTS


class PageAdmin(DisplayableAdmin):
    form_columns = list(DISPLAYABEL_DEFAULTS["form_columns"])
    form_columns.insert(0, "title")
    form_columns.insert(4, "parent")
    form_columns.insert(5, "slug")
    form_excluded_columns = DISPLAYABEL_DEFAULTS["form_excluded_columns"] + [
        "sort_order",
        "_sort_order",
    ]
    column_list = ["title", "status", "updated"]
    column_editable_list = ["title"]
    column_default_sort = ("sort_order", False)

    def edit_form(self, obj):
        return self.modify_edit_form(super(PageAdmin, self).edit_form(obj), page=obj)

    def modify_edit_form(self, form, page):
        form.parent.query_factory = lambda: Page.query.filter(Page.id != page.id)
        return form

    def get_preview_url(instance):
        return f"/{instance.slug_path}/"
