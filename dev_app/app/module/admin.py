from starlit.contrib.admin.core import DisplayableAdmin
from starlit.models import db
from starlit.babel import lazy_gettext
from .models import Page


class PageAdmin(DisplayableAdmin):
    form_rules = [(4, "content"), (5, "parent"), (6, "is_live"), (7, "must_show_in_menu"),]
    form_excluded_columns = ["children", "contenttype", "slug_path"]
    column_list = [(1, "parent")]


def register_admin(app, admin):
    admin.add_view(PageAdmin(
        Page,
        db.session,
        name=lazy_gettext('Pages'),
        menu_icon_type='fa',
        menu_icon_value='fa-book'
    ))
