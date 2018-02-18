from uuid import uuid4
from flask import current_app, request, url_for
from flask_babelex import get_locale
from starlit.babel import gettext, ngettext


_unique_string_cache = {}

def inject_language_info():
    lang = get_locale().language
    rtl = lang in ('ar', 'az', 'fa', 'he', 'ur', )
    return dict(lang=lang, rtl=rtl, _trans=gettext, _ntrans=ngettext)


def unique_string(s, length=7):
    """Useful for html id attribute generation"""
    def gen_unique_string(s, length):
        if not (0 < length <= 32):
            raise ValueError("Invalid value for unique string length: {}".format(length))
        return s + "-" + uuid4().hex[:length].lower()
    key = (str(s), length)
    if not key in _unique_string_cache:
        _unique_string_cache[key] = gen_unique_string(s, length)
    return _unique_string_cache[key]


def register_context_processors():
    context_processers = (
        inject_language_info,
    )
    for cp in context_processers:
        current_app.context_processor(cp)
    current_app.template_filter()(unique_string)
