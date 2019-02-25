# -*- coding: utf-8 -*-
"""
    oy.contrib.collect.cli
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The click command for this extension.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os
import click
from werkzeug import import_string
from flask import current_app
from flask.cli import with_appcontext


@click.command("collectstatic")
@click.argument("destination-directory", default="static", required=False)
@click.option(
    "--verbose", help="Show detailed info about copied files and folders.", default=True
)
@click.pass_context
@with_appcontext
def collect_static(ctx, destination_directory, verbose):
    """Collect static files of the application in one directory."""
    import_path = current_app.config["COLLECT_STORAGE"]
    storage_class = import_string(import_path, silent=True)
    if storage_class is None:
        click.secho(f"Could not import storage class: {import_path}", fg="red")
        raise click.Abort()
    storage = storage_class(
        app=current_app._get_current_object(),
        destdir=destination_directory,
        verbose=verbose,
    )
    click.secho("\r\n" + ("~" * 12), fg="yellow")
    click.echo(f"Collecting static files for app: {current_app.name}")
    click.echo(f"Using storage: {import_path}")
    storage.run()
    click.echo(f"Done copying files to {os.path.abspath(destination_directory)}")
    click.secho("\r\n" + ("~" * 12), fg="yellow")
