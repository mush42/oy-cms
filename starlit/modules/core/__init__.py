from sqlalchemy.orm.exc import NoResultFound
from flask import _request_ctx_stack, current_app, request
from starlit.globals import current_page, parent_page_class
from starlit.wrappers import StarlitModule
from starlit.util.slugging import PathToSlugConvertor

core = StarlitModule('core', __name__, builtin=True)

@core.record
def add_slug_url_convertor(state):
    state.app.url_map.converters['slug'] = PathToSlugConvertor

def pull_slug_path():
    _request_ctx_stack.top.requested_slug_path = request.path.strip('/')


@core.record_once
def add_slug_path(state):
    state.app.before_request(pull_slug_path)

@core.app_context_processor
def enject_pages():
    pages = parent_page_class.query.viewable.filter(
        parent_page_class.is_primary==True).filter(
        parent_page_class.slug_path!=current_app.config.get('HOME_SLUG')
    ).all()
    return dict(
        pages=pages,
        page=current_page
    )

@core.route('/<slug:slug_path>', endpoint='get_page_by_slug', methods=['GET', 'POST'])
def page_view(slug_path):
    if current_page is None:
        abort(404)
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
