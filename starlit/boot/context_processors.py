from uuid import uuid4
from flask import current_app, request, url_for
from flask_babelex import get_locale
from starlit.babel import gettext, ngettext


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


def unique_string(length=7):
    """Useful for html id attribute generation"""
    if not (0 < length <= 32):
        raise ValueError("Invalid value for unique string length: {}".format(length))
    return uuid4().hex[:length].lower()
    

def register_context_processors(app):
    context_processers = (
        inject_language_info,
        inject_should_enable_inline_editing,
    )
    for cp in context_processers:
        app.context_processor(cp)
    app.template_global(unique_string)