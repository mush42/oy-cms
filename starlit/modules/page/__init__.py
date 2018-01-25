from warnings import warn
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app, request, g, abort
from starlit.util.slugging import PathToSlugConvertor
from starlit.modules.page.templating import render_page_template
from starlit.util.option import Option
from starlit.babel import lazy_gettext
from .wrappers import PageModule, get_page
from .models import Page


page = PageModule(__name__, 'page')

@page.record
def add_slug_url_convertor(state):
    state.app.url_map.converters['slug'] = PathToSlugConvertor

@page.before_app_first_request
def warn_if_home_does_not_exist():
    if get_page(current_app.config.get('HOME_SLUG')) is None:
        pass
        #warn('Home page is not defined, your visitors will see a 404 error when they visit your site root')

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


@page.route('/<slug:slug>', endpoint='get_page_by_slug', methods=['GET', 'POST'])
def page_view(slug):
    if not g.page:
        abort(404)
    handler = page.get_handler_for(g.page.contenttype)
    template_args = {}
    if handler is not None:
        if request.method not in handler[1]:
            abort(405)
        rv = handler[0]()
        if isinstance(rv, dict):
            template_args.update(rv)
        else:
            return rv
    return render_page_template(context=template_args)

@page.route('/', endpoint='index')
def index():
    if not g.page:
        abort(404)
    return render_page_template()
