from flask import current_app, request, url_for
from flask_admin import helpers as admin_helpers
from flask_babelex import get_locale
from starlit.boot.exts.admin import admin
from starlit.babel import gettext, ngettext

def security_context_processor():
    if not request.blueprint == 'security':
        return {}
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
        _gettext= gettext,
        _trans= gettext
    )


def inject_language_info():
    lang = get_locale().language
    rtl = lang in ('ar', 'az', 'fa', 'he', 'ur', )
    return dict(lang=lang, rtl=rtl, _trans=gettext, _ntrans=ngettext)

def should_enable_inline_editing():
    if not current_app.config.get('ENABLE_INLINE_EDITING'):
        return False
    elif not current_user.is_authenticated or not current_user.is_active or not current_user.has_role('admin'):
        return False
    return True

def inject_should_enable_inline_editing():
    return dict(should_enable_inline_editing=should_enable_inline_editing())


def register_context_processors(app):
    context_processers = (inject_language_info, inject_should_enable_inline_editing, security_context_processor)
    for cp in context_processers:
        app.context_processor(cp)
