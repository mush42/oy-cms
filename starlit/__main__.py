# -*- coding: utf-8 -*-
"""
    starlit.main
    ~~~~~~~~~~~

    Contains global cli commands that aren't tied to
    a specific app instance.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
import os
import shutil
import click
from jinja2 import Environment, FileSystemLoader
from flask.helpers import get_root_path
from starlit.helpers import exec_module


class ProjectTemplateCopier:
    """Mirror a project template directory with all templates rendered"""

    def __init__(self, templatedir, distdir, project_name, ctx_build_vars=None):
        self.templatedir = templatedir
        self.distdir = distdir
        self.project_name = project_name
        self.jinja_env = Environment(loader=FileSystemLoader(self.templatedir))
        _build_ctx_mod_path = os.path.join(self.templatedir, 'build_context.py')
        if ctx_build_vars is None:
            ctx_build_vars = dict()
        ctx_build_vars.setdefault('appname', self.project_name)
        mod = exec_module(_build_ctx_mod_path, 'ctxb', ctx_build_vars)
        self.render_ctx = {}
        for attr in mod.__all__:
            self.render_ctx[attr] = getattr(mod, attr)

    def copy_rendered(self, t_file, o_file):
        """Render the given template to the output file"""
        click.echo(f"Copying {t_file} to {o_file}")
        relative_template = os.path.relpath(t_file, self.templatedir)
        template = self.jinja_env.get_template(relative_template)
        with open(o_file, 'w', encoding='utf8') as output:
            output.write(template.render(**self.render_ctx))

    def copy_all(self):
        shutil.copytree(
          self.templatedir,
          self.distdir,
          copy_function=self.copy_rendered
      )


def prepare_directory(directory):
    directory = os.path.join(os.getcwd(), directory)
    if os.path.isdir(directory) and os.listdir(directory):
        click.echo(f"Error: The folder {directory} already exists and is not empty.")
    return directory


@click.command()
@click.argument('project_name')
@click.option('--templatedir', help="The template to be used", default=None)
def create_project(project_name, templatedir=None):
    """Create a new starlit project"""
    if templatedir and not os.path.isdir(templatedir):
        click.echo(f"Error: Template directory {templatedir} does not exist.")
    if templatedir is None:
        templatedir = os.path.join(get_root_path('starlit'), 'project_template')
    click.echo(f"Creating project {project_name}...")
    click.echo(f"Using project template: {templatedir}...")
    copier = ProjectTemplateCopier(
        templatedir,
        prepare_directory(project_name),
        project_name
      ).copy_all()
