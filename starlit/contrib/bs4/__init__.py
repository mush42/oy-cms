# -*- coding: utf-8 -*-
"""
    starlit.contrib.bs4
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the minified css and js files of
    the latest version of bootstrap4 along
    with some helper jinja macros
"""
from starlit.wrappers import StarlitModule
from starlit.babel import lazy_gettext


BS4_CSS_URL = "https://stackpath.bootstrapcdn.com/bootswatch/4.1.2/materia/bootstrap.min.css"
BS4_JS_URL = "https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/js/bootstrap.bundle.min.js"
JQUERY_URL = "https://code.jquery.com/jquery-2.2.4.min.js"


bs4 = StarlitModule(
    'starlit.contrib.bs4',
    __name__,
    static_folder='static',
    template_folder='templates',
    viewable_name=lazy_gettext("Bootstrap")
  )


@bs4.settings_provider()
def provide_bs4_settings(app, module):
    return (
      {
       'name': 'bs4_use_cdn',
       'type': 'checkbox',
       'label': 'Load bootstrap assets from a content delivery network.',
       'default': not app.debug
      },
      {
        'name': 'bs4_cdn_css_url',
        'type': 'url',
        'label': 'Bootstrap CSS CDN URL',
        'default': BS4_CSS_URL,
      },
      {
        'name': 'bs4_cdn_js_url',
        'type': 'url',
        'label': 'Bootstrap javascript CDN URL',
        'default': BS4_JS_URL,
      },
      {
        'name': 'jquery_cdn_js_url',
        'type': 'url',
        'label': 'Jquery CDN URL',
        'default': JQUERY_URL,
      },
    )