from urllib.parse import urlencode
from werkzeug.exceptions import NotFound
from flask import current_app, request, _request_ctx_stack
from flask_babelex import get_locale
from oy.wrappers import OyModule
from oy.babel import gettext, ngettext, lazy_gettext
from .settings import current_settings_profile, current_settings


core = OyModule("oy.core", __name__, viewable_name=lazy_gettext("General"))


@core.app_context_processor
def register_context_processors():
    lang = get_locale().language
    rtl = lang in ("ar", "az", "fa", "he", "ur")
    return dict(
        lang=lang,
        rtl=rtl,
        _trans=gettext,
        _ntrans=ngettext,
        settings_profile=current_settings_profile,
        settings=current_settings,
    )


@core.app_template_filter()
def qs_args(url, qs):
    return "{}?".format(url) + urlencode(qs)


@core.settings_provider()
def provide_core_settings(app):
    return [
        dict(
            name="title",
            label=lazy_gettext("Site Title"),
            description=u"The site Title",
            type="text",
            default=u"Oy CMS",
        )
    ]
