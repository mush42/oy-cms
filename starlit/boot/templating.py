from starlit.util.helpers import prettify_date
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


def pretty_date(date):
    return prettify_date(date)

def args(url, qs):
    return '{}?'.format(url) + urlencode(qs)

def register_template_filters(app):
    template_filters = (pretty_date, args)
    for template_filter in template_filters:
        app.add_template_filter(template_filter)


