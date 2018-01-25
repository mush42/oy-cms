from werkzeug.routing import PathConverter
from slugify import slugify


class PathToSlugConvertor(PathConverter):
    def clean_slashes(self, path):
        return path.strip("/")

    def to_python(self, value):
        return self.clean_slashes(value)

    def to_url(self, value):
        return '/{}/'.format(value)

def split_slug(slug):
    slugs = slug.split('/')
    root = slugs[0]
    path = ''
    if len(slugs) >0:
        path = '/'.join(slugs[1:])
    return (root, path)
