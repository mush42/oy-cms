from flask import current_app, request, g, abort
from starlit.modules.page.templating import render_page_template
from starlit.util.option import Option
from starlit.babel import lazy_gettext
from .wrappers import PageModule
from .cli import install_fixtures_factory


page = PageModule('page',
    __name__,
    static_folder="static",
    template_folder="templates",
    builtin=True
  )

@page.record_once
def add_cli_command(state):
    state.app.cli.command(name='install-fixtures')(install_fixtures_factory(page.root_path))


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

