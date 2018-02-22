import re
from importlib import import_module
from pkgutil import iter_modules
from datetime import datetime
from dateutil.parser import parse
from .xlib.dateformat import pretty_date
from jinja2.utils import Markup


_email_re = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    flags=re.IGNORECASE
  )

def is_valid_email(email):
    """Return True if the supplied argument is a valid email"""
    return _email_re.match(email) is not None

def find_modules(basemodule, package_only=True):
    path = import_module(basemodule).__path__
    for importer, modname, ispkg in iter_modules(path):
        if modname.startswith('_') or (package_only and not ispkg):
            continue
        yield "%s.%s" %(basemodule, modname)

def import_modules(basemodule):
    packages = find_modules(basemodule)
    for module in (import_module(modname) for modname in packages):
        yield module


def get_method_in_all_bases(cls, meth_name, exclude=None):
    exclude = exclude or list()
    exclude += [object]
    bases = [c for c in cls.__mro__ if c not in exclude]
    for c in reversed(bases):
        meth = c.__dict__.get(meth_name, None)
        if meth is not None:
            yield meth


def prettify_date(s):
    date_time = s
    if isinstance(date_time, str):
        date_time = parse(s)
    return pretty_date(date_time)


def date_column_formatter(view, value):
    return prettify_date(value)

def make_summary(content, p=3):
    return ' '.join(Markup(content).striptags().split('.')[:p])

def date_stamp(date=None):
    if not date:
        date = datetime.now()
    return date.strftime('%y-%m-%d__%H-%M-%S')