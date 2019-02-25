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
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CopyOpts:
    src: str
    dst: str


class BaseStorage:
    """The base file storage.
    Concrete storages must implement the run() method.
    """

    def __init__(self, app, destdir, verbose):
        self.app = app
        self.destdir = Path(destdir)
        self.verbose = verbose

    def run(self):
        raise NotImplementedError

    def __iter__(self, src=None, dest=None):
        to_copy = []
        to_process = []
        if self.app.has_static_folder:
            to_process.append((self.app.static_folder, ""))
        blueprints = [bp for bp in self.app.blueprints.values() if bp.has_static_folder]
        for blueprint in blueprints:
            prefix = blueprint.static_url_path.lstrip(self.app.static_url_path).strip(
                "/"
            )
            to_process.append((blueprint.static_folder, prefix))
        for folder, prefix in to_process:
            for dirname, _, files in os.walk(folder):
                rel = Path(dirname).relative_to(folder)
                for file in files:
                    to_copy.append(
                        CopyOpts(
                            src=Path(dirname) / file,
                            dst=Path(self.destdir / prefix / rel / file),
                        )
                    )
        yield from to_copy
        with_prefix = [
            bp
            for bp in self.app.blueprints.values()
            if bp.has_static_folder and bp.url_prefix
        ]
        if with_prefix:
            self.log(
                f"Beside adding '{self.app.static_url_path}' to your static files webserver config."
            )
            self.log("You need to add the following aliases too:")
        for bp in with_prefix:
            self.log(f"  * '{bp.url_prefix}{bp.static_url_path}'")

    def log(self, msg):
        if self.verbose:
            click.echo(msg)
