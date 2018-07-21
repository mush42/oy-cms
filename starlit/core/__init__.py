from urllib.parse import urlencode
from werkzeug.exceptions import NotFound
from flask import current_app, request, _request_ctx_stack
from flask_babelex import get_locale
from starlit.wrappers import StarlitModule
from starlit.babel import gettext, ngettext, lazy_gettext
from starlit.slugging import PathToSlugConvertor
from .settings import current_settings_profile, current_settings


core = StarlitModule('starlit.core',
    __name__,
    template_folder='templates'
  )


@core.record_once
def configure_app(state):
    """Configure the app after blueprint registration."""
    state.app.url_map.converters['slug'] = PathToSlugConvertor

@core.app_context_processor
def register_context_processors():
    lang = get_locale().language
    rtl = lang in ('ar', 'az', 'fa', 'he', 'ur', )
    return dict(
        lang=lang,
        rtl=rtl,
        _trans=gettext,
        _ntrans=ngettext,
        settings_profile=current_settings_profile,
        settings=current_settings
    )

@core.app_template_filter()
def qs_args(url, qs):
    return '{}?'.format(url) + urlencode(qs)

@core.settings_provider()
def provide_page_settings(module):
    return [
        dict(
            name='title',
            label=lazy_gettext('Site Title'),
            description=u'The site Title',
            category='general',
            type='text',
            default=u'Starlit CMS'
        ),
    ]
