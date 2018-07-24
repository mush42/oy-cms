# -*- coding: utf-8 -*-
"""
    starlit.contrib.bs4
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the minified css and js files of
    the latest version of bootstrap4, either served
    directly or from a CDN). along with some helper
    jinja macros.
"""
from collections import namedtuple
from flask import url_for
from starlit.wrappers import StarlitModule
from starlit.babel import lazy_gettext
from starlit.core import current_settings


BS4_CDN_CSS_URL = "https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/css/bootstrap.min.css"
BS4_CDN_JS_URL = "https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/js/bootstrap.bundle.min.js"
JQUERY_CDN_URL = "https://code.jquery.com/jquery-2.2.4.min.js"


# Holds info about possible urls
bs4url = namedtuple('bs4_url', 'remote local')


bs4 = StarlitModule(
    'starlit.contrib.bs4',
    __name__,
    static_folder='static',
    template_folder='templates',
    viewable_name=lazy_gettext("Bootstrap")
  )


# maps resource types to url_info
_prefix = bs4.name.replace('.', '/')
resource_url = dict(
    jquery=bs4url(lambda: current_settings.jquerycdn, _prefix + '/js/jquery.min.js'),
    bs4css=bs4url(lambda: current_settings.bs4cdn_css, _prefix + '/css/bootstrap.min.css'),
    bs4js=bs4url(lambda: current_settings.bs4cdn_js, _prefix + '/js/bootstrap.min.js')
)
del _prefix


def bs4_url_for(restype):
    """Get the full url for the resource
        type (css, js, or jquery) based on 
        the current_settings.bs4_use_cdn
    """
    url_info = resource_url[restype]
    if current_settings.bs4_use_cdn:
        return url_info.remote()
    return url_for(bs4.name + '.static', filename=url_info.local)

@bs4.app_context_processor
def add_bs4_ctxp():
    return dict(bs4_url_for=bs4_url_for)


@bs4.settings_provider()
def provide_bs4_settings(app):
    return (
      {
       'name': 'bs4_use_cdn',
       'type': 'checkbox',
       'label': 'Load bootstrap assets from a content delivery network.',
       'default': not app.debug
      },
      {
        'name': 'bs4cdn_css',
        'type': 'url',
        'label': 'Bootstrap CSS CDN URL',
        'default': BS4_CDN_CSS_URL,
      },
      {
        'name': 'bs4cdn_js',
        'type': 'url',
        'label': 'Bootstrap javascript CDN URL',
        'default': BS4_CDN_JS_URL,
      },
      {
        'name': 'jquerycdn',
        'type': 'url',
        'label': 'Jquery CDN URL',
        'default': JQUERY_CDN_URL,
      },
    )


