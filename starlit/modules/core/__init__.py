from werkzeug.exceptions import NotFound
from flask import current_app, request, _request_ctx_stack
from starlit.globals import current_page, parent_page_class
from starlit.wrappers import StarlitModule
from starlit.util.slugging import PathToSlugConvertor
from .cli import install_fixtures, createsuperuser
from .templating import render_page_template


core = StarlitModule('core', __name__, builtin=True)


def page_view():
    handler = current_app.get_handler_for(current_page.contenttype)
    template_args = {}
    if handler is not None:
        _request_ctx_stack.top.module = handler.module
        if request.method not in handler.methods:
            abort(405)
        rv = handler.view_func()
        if isinstance(rv, dict):
            template_args.update(rv)
        else:
            return rv
    return render_page_template(context=template_args)


@core.record
def add_slug_url_convertor(state):
    state.app.url_map.converters['slug'] = PathToSlugConvertor


def set_page_and_response_if_appropriate():
    if isinstance(request.routing_exception, NotFound) and current_page:
        return page_view()


@core.record_once
def add_slug_path(state):
    state.app.before_request(set_page_and_response_if_appropriate)


@core.record_once
def add_cli_command(state):
    """Add starlit command line interface"""
    @state.app.cli.group(name='starlit')
    def starlit_group():
        """Perform tasks related to Starlit CMS"""
    
    starlit_group.command(name='install-fixtures')(install_fixtures)
    starlit_group.command(name='create-super-user')(createsuperuser)


@core.app_context_processor
def enject_pages():
    pages = parent_page_class.query.viewable.filter(
        parent_page_class.is_primary==True).filter(
        parent_page_class.slug_path!=current_app.config.get('HOME_SLUG')
    ).all()
    return dict(
        pages=pages,
        current_page=current_page,
        page=current_page
    )
