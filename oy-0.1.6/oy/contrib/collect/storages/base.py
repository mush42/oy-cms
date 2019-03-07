# -*- coding: utf-8 -*-
"""
    oy.contrib.collect.storages.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Implements the abstract base storage.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os
import click
from pathlib import PurePath as Path


class BaseStorage:
    """The base file storage.
    Concrete storages must implement the run() method.
    """

    # A human readable name to describe this storage
    name = None

    def __init__(self, app, destdir, verbose):
        self.app = app
        self.destdir = Path(destdir)
        self.verbose = verbose

    def run(self):
        raise NotImplementedError

    def __iter__(self):
        to_copy = set()
        to_process = set()
        if self.app.has_static_folder:
            to_process.add((self.app.static_folder, ""))
        blueprints = [bp for bp in self.app.blueprints.values() if bp.has_static_folder]
        for blueprint in blueprints:
            if blueprint.url_prefix:
                prefix = "/".join(
                    p.strip("/")
                    for p in (blueprint.url_prefix, blueprint.static_url_path)
                )
            else:
                pathcomp = [p for p in blueprint.static_url_path.split("/") if p][1:]
                prefix = "/".join(pathcomp).strip("/")
            to_process.add((blueprint.static_folder, prefix))
        for folder, prefix in to_process:
            for dirname, _, files in os.walk(folder):
                for file in files:
                    relpath = Path(dirname, file).relative_to(folder)
                    src = Path(dirname) / file
                    dst = self.destdir / prefix / relpath
                    to_copy.add((src, dst))
        yield from to_copy
        with_prefix = [
            bp
            for bp in self.app.blueprints.values()
            if bp.has_static_folder and bp.url_prefix
        ]
        if with_prefix:
            app_static = self.app.static_url_path.strip("/")
            self.log(
                f"\r\n\r\nBeside adding '{app_static}' to your static files webserver config."
            )
            self.log("You need to add aliases for the following as well:")
        for bp in with_prefix:
            uri = bp.url_prefix + bp.static_url_path
            self.log(f"  *  url='{uri}', folder='{(self.destdir/uri[1:]).as_posix()}'")

    def log(self, msg):
        if self.verbose:
            click.echo(msg)
