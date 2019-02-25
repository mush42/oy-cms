# -*- coding: utf-8 -*-
"""
    oy.contrib.collect.storages.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Implements the local file system base storage.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os
import shutil
from .base import BaseStorage


class LocalFileSystemStorage(BaseStorage):
    def run(self):
        for cop in self:
            parent = cop.dst.parent
            if not parent.is_dir():
                parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(cop.src, cop.dst, follow_symlinks=False)
