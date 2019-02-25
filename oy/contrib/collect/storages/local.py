# -*- coding: utf-8 -*-
"""
    oy.contrib.collect.storages.local
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Implements the local file system base storage.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os
import shutil
from pathlib import Path
from .base import BaseStorage


class LocalFileSystemStorage(BaseStorage):

    def run(self):
        for src, dst in self:
            src, dst = Path(src), Path(dst)
            parent = dst.parent
            if not parent.is_dir():
                parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst, follow_symlinks=False)
