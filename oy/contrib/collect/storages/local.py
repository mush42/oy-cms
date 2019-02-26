# -*- coding: utf-8 -*-
"""
    oy.contrib.collect.storages.local
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Implements the local file system base storage.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import shutil
from pathlib import Path
from .base import BaseStorage


class LocalFileSystemStorage(BaseStorage):

    name = "Local File System Storage"

    def run(self):
        for src, dst in self:
            src, dst = Path(src), Path(dst)
            if dst.exists() and (src.stat().st_mtime < dst.stat().st_mtime):
                self.log(
                    f"Ignoring file {src}. The recent version of the file already exists in the destination directory."
                )
                continue
            parent = dst.parent
            if not parent.is_dir():
                parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst, follow_symlinks=False)
            self.log(f"Copied {src} to {dst}.")
