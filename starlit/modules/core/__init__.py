from sqlalchemy.orm.exc import NoResultFound
from flask import _request_ctx_stack, current_app, request
from starlit.globals import current_page, parent_page_class
from starlit.wrappers import StarlitModule
from starlit.util.slugging import PathToSlugConvertor
#from .cli import install_fixtures
from .templating import render_page_template


core = StarlitModule('core', __name__, builtin=True)


def page_view():
    handler = current_app.get_handler_for(current_page.contenttype)
    template_args = {}
    if handler is not None:
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
    _request_ctx_stack.top.requested_slug_path = request.path.strip('/')
    if request.routing_exception is not None and current_page:
        return page_view()


@core.record_once
def add_slug_path(state):
    state.app.before_request(set_page_and_response_if_appropriate)


@core.record_once
def add_cli_command(state):
    pass
    #state.app.cli.command(name='install-fixtures')(install_fixtures)


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
