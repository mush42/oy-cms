from werkzeug.utils import import_string


def get_model(name):
    return import_string('starlit.models.%s' %name)
