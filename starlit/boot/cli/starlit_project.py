# -*- coding: utf-8 -*-
"""
    starlit.main
    ~~~~~~~~~~~

    Contains global cli commands that aren't tied to
    a specific app instance.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
import itertools
import keyword
import os
import re
import shutil
import click
from jinja2 import Template, Environment, FileSystemLoader
from flask.helpers import get_root_path
from starlit.helpers import exec_module
from ._vcs import get_vcs_from_url, clone


identifier = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)


class ProjectTemplateCopier:
    """Mirror a project template directory with all templates rendered"""

    def __init__(self, templatedir, distdir, project_name, ctx_build_vars=None):
        self.templatedir = templatedir
        self.distdir = distdir
        self.project_name = project_name
        self.jinja_env = Environment(loader=FileSystemLoader(self.templatedir))
        _build_ctx_mod_path = os.path.join(self.templatedir, "build_context.py")
        if ctx_build_vars is None:
            ctx_build_vars = {}
        ctx_build_vars.setdefault("project_name", self.project_name)
        mod = exec_module(_build_ctx_mod_path, "ctxb", ctx_build_vars)
        self.render_ctx = {"project_name": self.project_name}
        for attr in mod.__all__:
            self.render_ctx[attr] = getattr(mod, attr)

    def copy_rendered(self, src, dst, *, follow_symlinks=False):
        """Render the given template to the output file"""
        t_file = os.path.relpath(src, self.templatedir)
        # TODO: Find a better way to handle back-slashes
        t_file = "/".join(os.path.split(t_file))
        template = self.jinja_env.get_template(t_file)
        with open(dst, "w", encoding="utf8") as o_file:
            rendered = template.render(**self.render_ctx)
            o_file.write(rendered)
        return dst

    def copy_all(self):
        shutil.copytree(
            self.templatedir, self.distdir, copy_function=self.copy_rendered
        )
        self.post_copy()

    def post_copy(self):
        for root, dirnames, files in os.walk(self.distdir):
            for f in itertools.chain(dirnames, files):
                if self.jinja_env.variable_start_string in f:
                    newname = Template(f).render(**self.render_ctx)
                    pjoin = lambda p: os.path.join(root, p)
                    os.rename(pjoin(f), pjoin(newname))
        os.unlink(os.path.join(self.distdir, "build_context.py"))


def is_valid_identifier(project_name):
    """Check that the project name is a valid python identifier"""
    if keyword.iskeyword(project_name):
        return False
    return identifier.match(project_name) is not None


def prepare_directory(directory):
    directory = os.path.join(os.getcwd(), directory)
    if os.path.isdir(directory) and os.listdir(directory):
        click.echo(f"Error: The folder {directory} already exists and is not empty.")
        raise click.Abort()
    return directory


@click.command()
@click.argument("project_name")
@click.option("--templatedir", help="The template to be used", default=None)
def create_project(project_name, templatedir=None):
    """Create a new starlit project"""
    if not is_valid_identifier(project_name):
        click.echo(
            f"{project_name} is not valid as a project name. \r\n\
            Please use a valid python identifier, consisting only of \
            numbers, letters, and underscores."
        )
        raise click.Abort()
    if templatedir is None:
        templatedir = os.path.join(get_root_path("starlit"), "project_template")
    else:
        rv = get_vcs_from_url(templatedir)
        if rv is not None:
            click.echo(f"Cloning template from {rv.url}...")
            templatedir = clone(rv.url)
    if not os.path.isdir(templatedir):
        click.echo(f"Error: Template directory {templatedir} does not exist.")
        raise click.Abort()
    templates = []
    for f in os.listdir(templatedir):
        if os.path.isdir(os.path.join(templatedir, f)):
            if os.path.isfile(os.path.join(templatedir, f, "build_context.py")):
                templates.append(f)
    if templates and len(templates) > 1:
        rv = ""
        click.echo("Which template you would like to use?\r\n")
        for i in templates:
            click.echo(f"  * {i}")
        while rv not in templates:
            rv = click.prompt("\r\nPlease choose one of the above: ", default="default")
        templatedir = os.path.join(templatedir, rv)
    else:
        templatedir = os.path.join(templatedir, templates[0])
    click.echo(f"Creating project {project_name}...")
    click.echo(f"Using project template: {templatedir}...")
    copier = ProjectTemplateCopier(
        templatedir, prepare_directory(project_name), project_name
    ).copy_all()
    click.echo(f"\r\n.........................\r\n")
    click.echo(f"New project created at {self.distdir}")
