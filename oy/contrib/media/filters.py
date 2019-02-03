# -*- coding: utf-8 -*-
"""
    oy.contrib.media.filters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides file processors and filters for `filedepot` FileUploadField.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os.path
import fleep
from depot.fields.interfaces import FileFilter
from depot.io.utils import file_from_content
from io import BytesIO
from PIL import Image
from tempfile import TemporaryDirectory
from oy.models import db
from oy.babel import lazy_gettext


# See fleep supported file types <https://github.com/floyernick/fleep-py>
SUPPORTED_FILE_TYPES = {
    "raster-image": lazy_gettext("Image Files"),
    "raw-image": lazy_gettext("Raw Image Files"),
    "3d-image": lazy_gettext("3D Image Files"),
    "vector-image": lazy_gettext("Vector Image Files"),
    "video": lazy_gettext("Video Files"),
    "audio": lazy_gettext("Audio Files"),
    "document": lazy_gettext("Documents"),
    "executable": lazy_gettext("Executable Files"),
    "system": lazy_gettext("System Files"),
    "database": lazy_gettext("Database Files"),
    "archive": lazy_gettext("Archives"),
    "font": lazy_gettext("Font Files"),
}


class UnsupportedFileTypeError(IOError):
    """Raised when a filetype is not supported."""

    def __init__(self, filetypes, message=None):
        self.filetypes = filetypes
        self.message = message or lazy_gettext("Unsupported file type.")

    def __str__(self):
        readable_filetypes = []
        for ft in self.filetypes:
            readable_filetypes.append(SUPPORTED_FILE_TYPES.get(ft, ft))
        return (
            self.message
            + " "
            + lazy_gettext(
                "Please make sure you uploaded one of the following file types:"
            )
            + " "
            + ", ".join([str(ft) for ft in readable_filetypes])
        )


class FileTypeCheckFilter(FileFilter):
    """Checks that the given file is of a certain type."""

    def __init__(self, filetypes):
        self.filetypes = filetypes

    def validate_filetype(self, file):
        info = fleep.get(file.read(128))
        if not any(info.type_matches(ft) for ft in self.filetypes):
            db.session.rollback()
            raise UnsupportedFileTypeError(filetypes=self.filetypes)
        try:
            file.seek(0)
        except:
            pass

    def on_save(self, uploaded_file):
        fp = file_from_content(uploaded_file.original_content)
        self.validate_filetype(fp)


class WithThumbnailFilter(FileFilter):
    """ Uploads a thumbnail together with the file.

    Takes for granted that the file is an image.

    The resulting uploaded file will provide an additional property
    ``thumbnail_name``, which will contain the id and the path to the
    thumbnail. The name is replaced with the name given to the filter.

    .. warning::

        Requires Pillow library

    """

    quality = 90

    def __init__(self, name, size, format):
        self.name = name
        self.size = size
        self.format = format.lower()

    def get_image_size(self, image):
        return tuple("{}px".format(d) for d in image.size)

    def generate_thumbnail(self, fp):
        output = BytesIO()
        thumbnail = Image.open(fp)
        thumbnail.thumbnail(self.size, Image.LANCZOS)
        thumbnail = thumbnail.convert("RGBA")
        thumbnail.format = self.format
        thumbnail.save(output, self.format, quality=self.quality)
        output.seek(0)
        return output

    def store_thumbnail(self, uploaded_file, fp):
        name = f"thumbnail_{self.name}"
        original_filename = os.path.splitext(uploaded_file.file.name)[0]
        filename = f"{original_filename}-thumbnail-{self.name}.{self.format}"
        path, id = uploaded_file.store_content(fp, filename)
        uploaded_file[name] = {
            "id": id,
            "path": path,
            "size": self.get_image_size(Image.open(fp)),
        }

    def on_save(self, uploaded_file):
        fp = file_from_content(uploaded_file.original_content)
        self.store_thumbnail(uploaded_file, self.generate_thumbnail(fp))
