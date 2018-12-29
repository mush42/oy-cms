from slugify import slugify


def split_slug(slug):
    slugs = slug.split("/")
    root = slugs[0]
    path = ""
    if len(slugs) > 0:
        path = "/".join(slugs[1:])
    return (root, path)
