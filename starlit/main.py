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
import jinja2


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
def create_project(project_name):
    """Create a new starlit project"""
    directory = prepare_directory(project_name)

#--------------------
from jinja2 import Environment, PackageLoader, select_autoescape

starlit_pkg_loader = PackageLoader(
    'starlit',
    package_path='project_template'
)

env = Environment(loader=starlit_pkg_loader)
