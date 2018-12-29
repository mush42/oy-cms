from werkzeug.utils import import_string
from flask import current_app, request, session
from flask_babelex import Babel

babel = Babel()


def gettext(string, **variables):
    return string % variables


def ngettext(singular, plural, num, **variables):
    variables.setdefault("num", num)
    return (singular if num == 1 else plural) % variables


def lazy_gettext(string, **variables):
    return gettext(string, **variables)


try:
    from flask_babelex import Domain
except ImportError:

    class Translations(object):
        """Dummy Translations class for WTForms, no translation support."""

        def gettext(self, string):
            return string

        def ngettext(self, singular, plural, n):
            return singular if n == 1 else plural


else:

    class CustomDomain(Domain):
        def __init__(self, app):
            self.app = app
            self.dirname = app.root_path
            super(CustomDomain, self).__init__(
                self.get_translations_path(None), domain="oy"
            )

        def translation_path_from_config(self):
            try:
                return import_string(
                    self.app.config.get("TRANSLATIONS_PATH", "")
                ).__path__[0]
            except ValueError:
                return


@babel.localeselector
def get_locale():
    lang = request.args.get("lang")
    lang = lang or session.get("lang")
    supported_langs = current_app.config["DEFAULT_LOCALE"]
    if lang and lang in supported_langs:
        return lang
    return request.accept_languages.best_match(supported_langs)


def init_babel(app):
    global gettext, ngettext, lazy_gettext
    babel.init_app(app)
    domain = CustomDomain(app)
    gettext = domain.gettext
    ngettext = domain.ngettext
    lazy_gettext = domain.lazy_gettext
    try:
        from wtforms.i18n import messages_path
    except ImportError:
        from wtforms.ext.i18n.utils import messages_path
    wtforms_domain = Domain(messages_path(), domain="wtforms")

    class Translations(object):
        """Fixes WTForms translation support and uses wtforms translations."""

        def gettext(self, string):
            t = wtforms_domain.get_translations()
            return t.ugettext(string)

        def ngettext(self, singular, plural, n):
            t = wtforms_domain.get_translations()
            return t.ungettext(singular, plural, n)
