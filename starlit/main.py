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
import click
from jinja2 import (
    Environment, PackageLoader,
    FileSystemLoader, select_autoescape
  )


def prepare_directory(directory):
    directory = os.path.join(os.path.abspath(directory)
    if not os.path.isdir(directory):
        if os.path.isfile(directory):
            raise FileExistsError(f"{directory} is not a directory.")
        os.mkdir(directory)
    if os.listdir(directory):
        raise FileExistsError(f"The folder {directory} already exists and is not empty.")
    return directory


@click.command()
@click.argument('project_name', help="The name of the project  to create")
@click.option('templatedir', help="The path to the template to be used")
def create_project(project_name, templatedir=None):
    """Create a new starlit project"""
    if templatedir and not os.path.isdir(templatedir):
        raise FileNotFoundError(f"Template directory {templatedir} does not exist.")
    targetdir = prepare_directory(project_name)
    jinja_loader = PackageLoader('starlit', package_path='project_template')
    if templatedir:
        jinja_loader = FileSystemLoader(templatedir)
    jinja_env = Environment(loader=jinja_loader)
    for dirpath, dirnames, filenames in os.walk():


