from flask import request, render_template, _request_ctx_stack
from starlit.globals import current_page


def templates_for_page(page):
    if page.is_home:
        return 'site/index.html'
    slug = page.slug_path
    templates = ["page", page.__contenttype__] + slug.split('/')
    templates.reverse()
    built_tpl_path = lambda prefix: [prefix + '{}.html'.format(t) for t in templates]
    rv = []
    if _request_ctx_stack.top.module:
        rv.extend(built_tpl_path(_request_ctx_stack.top.module + '/'))
    return rv + built_tpl_path('site/page/')
    

def render_page_template(page=None, context=None, template=None):
    page = page or current_page
    context = context or dict()
    context.setdefault('page', page)
    if not template:
        template = templates_for_page(page)
    return render_template(template, **context)

