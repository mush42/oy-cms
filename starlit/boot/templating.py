from flask import current_app
from starlit.util.helpers import prettify_date
from urllib.parse import urlencode


def pretty_date(date):
    return prettify_date(date)

def args(url, qs):
    return '{}?'.format(url) + urlencode(qs)

def register_template_filters():
    template_filters = (pretty_date, args)
    for template_filter in template_filters:
        current_app.add_template_filter(template_filter)

