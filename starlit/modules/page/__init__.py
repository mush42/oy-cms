from starlit.wrappers import StarlitModule
from starlit.util.option import Option
from starlit.babel import lazy_gettext
from .models import *


page = StarlitModule('page',
    __name__,
    static_folder="static",
    template_folder="templates",
    builtin=True
  )


@page.settings_provider
def provide_page_settings():
    return [
        Option(u'title',
            label=lazy_gettext('Site Title'),
            description=u'The site Title',
            category='general',
            type='text',
            default=u'Starlit CMS'
        )
    ]

