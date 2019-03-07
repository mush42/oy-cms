# -*- coding: utf-8 -*-
"""
    oy.boot.cli.oyinit
    ~~~~~~~~~~~

    Offers commands to create a project using a configurable template.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
import itertools
import keyword
import os
import re
import shutil
import click
from contextlib import suppress
from jinja2 import Template, Environment, FileSystemLoader
from flask.helpers import get_root_path
from oy.helpers import exec_module
from . import oy_group
from ._vcs import get_vcs_from_url, clone


def is_valid_pkg_name(pkg_name):
    """Check that the given name is a valid python package name."""
    if keyword.iskeyword(pkg_name):
        return False
    return pkg_name.isidentifier()


def prepare_directory(directory):
    directory = os.path.join(os.getcwd(), directory)
    if os.path.isdir(directory) and os.listdir(directory):
        click.echo(f"Error: The folder {directory} already exists and is not empty.")
        raise click.Abort()
    return directory


class ProjectTemplateCopier:
    """Mirror a project template directory with all templates rendered"""

    def __init__(self, templatedir, distdir, project_name, ctx_build_vars=None):
        self.templatedir = templatedir
        self.distdir = distdir
        self.project_name = project_name
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templatedir),
            block_start_string="[%",
            block_end_string="%]",
            variable_start_string="[[",
            variable_end_string="]]",
            optimized=False,
        )
        _build_ctx_mod_path = os.path.join(self.templatedir, "build_context.py")
        if ctx_build_vars is None:
            ctx_build_vars = {}
        ctx_build_vars.setdefault("project_name", self.project_name)
        mod = exec_module(_build_ctx_mod_path, "ctxb", ctx_build_vars)
        self.render_ctx = {"project_name": self.project_name}
        for attr in mod.__all__:
            self.render_ctx[attr] = getattr(mod, attr)

    def copy_all(self):
        try:
            self.mirror_tree(self.templatedir, self.distdir)
        except Exception as e:
            if os.path.isdir(self.distdir):
                os.unlink(self.distdir)
            raise e
        else:
            os.unlink(os.path.join(self.distdir, "build_context.py"))
            with suppress(IOError):
                os.rmdir(os.path.join(self.distdir, "__pycache__"))

    def render_name(self, name, basedir):
        if self.jinja_env.variable_start_string in name:
            name = self.jinja_env.from_string(name, globals=self.render_ctx).render()
        return os.path.join(basedir, os.path.normpath(name))

    def mirror_tree(self, src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)
        names = os.listdir(src)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = self.render_name(name, dst)
            if os.path.isdir(srcname):
                self.mirror_tree(srcname, dstname)
            elif os.path.isfile(srcname):
                if srcname.endswith(".tpl"):
                    t_file = os.path.relpath(srcname, self.templatedir)
                    if os.path.sep == "\\":
                        t_file = "/".join(t_file.split("\\"))
                    template = self.jinja_env.get_template(
                        t_file, globals=self.render_ctx
                    )
                    with open(dstname[:-4], "w", encoding="utf8") as o_file:
                        o_file.write(template.render())
                else:
                    shutil.copy(srcname, dstname)


@click.command(name="oyinit")
@click.argument("project_name")
@click.option(
    "--templatedir", help="Template directory or repository URL.", default=None
)
@click.option(
    "--templatename",
    help="The name of the template you want to use.",
    default="default",
)
def init_oy_project(project_name, templatedir, templatename):
    """Start a new oy project"""
    if not is_valid_pkg_name(project_name):
        click.echo(
            f"{project_name} is not valid as a project name. \r\n\
            Please use a valid python identifier."
        )
        raise click.Abort()
    if templatedir is None:
        templatedir = os.path.join(get_root_path("oy"), "project_templates")
    else:
        rv = get_vcs_from_url(templatedir)
        if rv is not None:
            click.secho(f"Cloning template from {rv.url}...", fg="yellow")
            cloned = clone(rv)
            if not cloned:
                click.secho(f"Error cloning repository from {rv.url}.", fg="red")
                raise click.Abort()
            templatedir = os.path.join(cloned, "project_templates")
            click.secho("Repository cloned successfully.", fg="yellow")
    if not os.path.isdir(templatedir):
        click.echo(f"Error: Template directory {templatedir} does not exist.")
        raise click.Abort()
    templatepath = os.path.join(templatedir, templatename)
    if not os.path.exists(templatepath):
        click.secho(f"Template {templatename} does not exists.", fg="red")
        raise click.Abort()
    click.echo(
        f"\r\nCreating a new project called `{project_name}` from `{templatedir}`"
    )
    click.echo(f"Using project template: {templatename}.")
    distdir = prepare_directory(project_name)
    copier = ProjectTemplateCopier(templatepath, distdir, project_name).copy_all()
    click.echo("~" * 12)
    click.secho(f"New project created at {distdir}\r\n", fg="green", bold=True)
