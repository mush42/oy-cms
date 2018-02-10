from warnings import warn
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app, request, g, abort
from starlit.util.slugging import PathToSlugConvertor
from starlit.modules.page.templating import render_page_template
from starlit.util.option import Option
from starlit.babel import lazy_gettext
from .wrappers import PageModule
from .models import Page
from .cli import install_fixtures_factory


page = PageModule('page',
    __name__,
    static_folder="static",
    template_folder="templates",
    builtin=True
  )


@page.record
def add_slug_url_convertor(state):
    state.app.url_map.converters['slug'] = PathToSlugConvertor

@page.after_setup
def add_cli_command(app):
    app.cli.command(name='install-fixtures')(install_fixtures_factory(page.root_path))


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

@page.app_context_processor
def enject_pages():
    pages = Page.query.viewable.filter(Page.is_primary==True).filter(Page.slug_path!=current_app.config.get('HOME_SLUG')).all()
    return dict(pages=pages)


def get_page(slug_path):
    return Page.query.viewable.filter(Page.slug_path==slug_path).one_or_none()


@page.route('/<slug:slug_path>', endpoint='get_page_by_slug', methods=['GET', 'POST'])
def page_view(slug_path):
    if not slug_path:
        slug_path = current_app.config.get('HOME_SLUG')
    slug = slug_path.strip('/')
    requested_page = get_page(slug)
    if requested_page is None:
        abort(404)
    g.page = requested_page
    setattr(g, requested_page.contenttype, requested_page)
    handler = page.get_handler_for(requested_page.contenttype)
    template_args = {}
    if handler is not None:
        if request.method not in handler.methods:
            abort(405)
        rv = handler.view_func()
        if isinstance(rv, dict):
            template_args.update(rv)
        else:
            return rv
    return render_page_template(page=requested_page, context=template_args)

@page.route('/', endpoint='index')
def index():
    return page_view(slug_path=current_app.config['HOME_SLUG'])
