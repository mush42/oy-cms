# -*- coding: utf-8 -*-
"""
    oy.contrib.media.utils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides file processors and filters for `filedepot` FileUploadField.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import os.path
import fleep
from tempfile import SpooledTemporaryFile
from PIL import Image
from depot.io.utils import file_from_content, INMEMORY_FILESIZE
from depot.fields.interfaces import FileFilter
from depot.fields.upload import UploadedFile
from depot.io.interfaces import FileStorage
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


class UploadedImage(UploadedFile):
    """ Uploads a thumbnail together with the file.
    Takes for granted that the file is an image.
    The resulting uploaded file will provide an additional property
    ``thumbnail_name``, which will contain the id and the path to the
    thumbnail. The name is replaced with the name given to the filter.
    .. warning::
        Requires Pillow library
    """
    
    # Those attributes should be overridden by the inheriting classes
    thumbnail_sizes = {}
    thumbnail_quality = 90
    thumbnail_format = "png"

    def process_content(self, content, filename=None, content_type=None):
        file = file_from_content(content)
        FileTypeCheckFilter(filetypes=["raster-image", "raw-image", "vector-image"]).validate_filetype(file)
        __, filename, content_type = FileStorage.fileinfo(content)
        for name, size in self.thumbnail_sizes.items():
            self.store_thumbnail(file, filename, name, size)
        content.seek(0)
        super().process_content(content, filename, content_type)

    def store_thumbnail(self, file, original_file_name, thumb_name, thumb_size):
        name = f"thumbnail_{thumb_name}"
        image_filename = os.path.splitext(original_file_name)[0]
        filename = f"{image_filename}-thumbnail-{thumb_name}.{self.thumbnail_format}"
        thumbnail_file = self.generate_thumbnail(file, thumb_size)
        path, id = self.store_content(thumbnail_file, filename)
        self[name] = {
            "id": id,
            "path": path,
            "size": self.get_image_size(Image.open(thumbnail_file)),
        }

    def generate_thumbnail(self, fp, thumb_size):
        output = SpooledTemporaryFile(INMEMORY_FILESIZE)
        thumbnail = Image.open(fp)
        thumbnail.thumbnail(thumb_size, Image.LANCZOS)
        thumbnail = thumbnail.convert("RGBA")
        thumbnail.format = self.thumbnail_format
        thumbnail.save(output, self.thumbnail_format, quality=self.thumbnail_quality)
        fp.seek(0)
        output.seek(0)
        return output

    def get_image_size(self, image):
        return tuple("{}px".format(d) for d in image.size)

    def get_thumbnail(self, size):
        """ Returns the thumbnail file with the given size (e.g. 'sm').
        """
        name = f"thumbnail_{size}"
        if name not in self:
            return
        return self.depot.get(self[name]["id"])


def uploaded_image(thumbnail_sizes, thumbnail_format="png", thumbnail_quality=90):
    """A factory function which help to avoid the need to inherit the UploadedImage class."""
    return type("UploadedImageUploadType", (UploadedImage,), dict(
        thumbnail_sizes=thumbnail_sizes,
        thumbnail_format=thumbnail_format,
        thumbnail_quality=thumbnail_quality
    ))