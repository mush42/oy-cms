from flask_admin.form import SecureForm
from starlit.boot.exts.sqla import db
from starlit.babel import gettext, lazy_gettext
from starlit.modules.core.models import Site
from starlit.boot.exts.admin import admin, StarlitModelView

def active_formatter(view, context, model, name):
    if getattr(model, name):
        return gettext("Yes")
    return gettext("No")


class SiteAdmin(StarlitModelView):
    can_view_details = True
    # Edit in a dialog not in a new page.
    edit_modal = True
    details_modal = True
    # Enable CSRF protection.
    form_base_class = SecureForm
    form_excluded_columns = ['settings']
    # How many entries to display per page?
    page_size = 5
    # Column formatters.
    column_formatters = {'is_active': active_formatter}
    column_default_sort = ("is_active", True)
    column_editable_list = ["name"]

admin.add_view(SiteAdmin(Site, db.session, name=lazy_gettext('Sites'), menu_icon_type='fa', menu_icon_value='fa-flag'))