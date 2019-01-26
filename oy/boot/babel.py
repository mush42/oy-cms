from werkzeug.utils import import_string
from flask import current_app, request, session
from flask_babelex import Babel, Domain
from oy import translations


class OyDomain(Domain):
    def __init__(self):
        super().__init__(translations.__path__[0], domain="oy")

    def get_translations_path(self, ctx):
        transconf = self.translation_path_from_config()
        if transconf:
            return transconf
        return super().get_translations_path(ctx)

    def translation_path_from_config(self):
        try:
            return import_string(
                current_app.config.get("OY_TRANSLATIONS_PATH", "")
            ).__path__[0]
        except ValueError:
            return


oy_domain = OyDomain()
gettext = oy_domain.gettext
ngettext = oy_domain.ngettext
lazy_gettext = oy_domain.lazy_gettext
babel = Babel()


@babel.localeselector
def get_locale():
    lang = request.args.get("lang")
    lang = lang or session.get("lang")
    supported_langs = current_app.config["DEFAULT_LOCALE"]
    if lang and lang in supported_langs:
        return lang
    return request.accept_languages.best_match(supported_langs)
