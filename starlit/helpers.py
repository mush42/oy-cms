import types
import re
from importlib import import_module
from pkgutil import iter_modules
from datetime import datetime
from flask import request


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


def date_stamp(date=None):
    if not date:
        date = datetime.now()
    return date.strftime('%y-%m-%d__%H-%M-%S')


def paginate_with_args(query, page_arg='page', perpage_arg='item_count', default_perpage=10):
    page = int(request.args.get(page_arg, 1))
    perpage = int(request.args.get(perpage_arg, default_perpage))
    return query.paginate(page, perpage, False)


def exec_module(filename, mod_name, globals=None):
    d = types.ModuleType(mod_name)
    d.__file__ = filename
    try:
        if globals is not None:
            d.__dict__.update(globals)
        with open(filename, mode='rb') as module:
            exec(compile(module.read(), filename, 'exec'), d.__dict__)
        return d
    except IOError:
        raise FileNotFoundError(f"{filename} does not exist")
