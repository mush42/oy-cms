# -*- coding: utf-8 -*-
"""
    oy.contrib.demo_content
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Allows you to add some demo content.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.contrib.extbase import OyExtBase
from .cli import FixtureInstaller, install_fixtures, create_all


class DemoContent(OyExtBase):

    module_args = dict(
        name="oy.contrib.demo_content", import_name="oy.contrib.demo_content"
    )

    def init_app(self, app):
        app.cli.add_command(install_fixtures)
        app.cli.add_command(create_all)
