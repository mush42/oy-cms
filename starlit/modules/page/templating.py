from flask import g, render_template

def templates_for_page(page):
    if page.is_home:
        return 'starlit/site/index.html'
    slug = page.slug_path
    templates = ["page", page.__contenttype__] + slug.split('/')
    templates.reverse()
    return ['starlit/site/page/{}.html'.format(t) for t in templates]

def render_page_template(page=None, context=None, template=None):
    page = g.page
    context = context or dict()
    context.setdefault('page', page)
    if not template:
        template = templates_for_page(page)
    return render_template(template, **context)

