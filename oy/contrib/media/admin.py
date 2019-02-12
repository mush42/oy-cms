# -*- coding: utf-8 -*-
"""
    oy.contrib.media.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the admin interface for adding and removing images and documents.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from depot.manager import DepotManager
from depot.middleware import FileServeApp
from depot.fields.upload import UploadedFile
from werkzeug.datastructures import FileStorage
from flask import flash, request, abort, url_for, redirect
from flask_admin import expose
from flask_admin.model.template import EndpointLinkRowAction
from oy.contrib.admin import OyModelView
from oy.contrib.admin.fields import BootstrapFileInputField, TagsField
from oy.models import db
from oy.babel import gettext, lazy_gettext
from .models import Image, Document
from .serving import ModelFileServer
from .filters import FileTypeCheckFilter, UnsupportedFileTypeError


class GenericMediaAdmin(OyModelView):
    list_template = "oy/contrib/media/admin/list.html"
    form_columns = ["title", "tags", "uploaded_file", "description",]
    form_extra_fields = dict(tags=TagsField(label=lazy_gettext("Tags")),)
    form_overrides = dict(uploaded_file=BootstrapFileInputField)
    form_widget_args = dict(uploaded_file=dict(required=False))
    column_list = ["title", "created"]
    column_searchable_list = ["tags", "title", "description"]
    column_extra_row_actions = [
        EndpointLinkRowAction(
            "fa fa-download", ".serve_file_with_id", title=lazy_gettext("Download")
        )
    ]

    @property
    def extra_js(self):
        return [url_for("oy.contrib.media.static", filename="js/media-view.js"),]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_storage = DepotManager.get(self.model.get_upload_storage())
        self.fileserver = ModelFileServer(model=self.model)

    def search_placeholder(self):
        return gettext("Search")

    @expose("/download/<id>")
    def serve_file_with_id(self, id):
        return self.fileserver(file_id=self.get_one(id).file_id)

    @expose("/files/<string:file_id>")
    def internal_serve(self, file_id):
        return self.fileserver(file_id=file_id)

    def is_valid_file_type(self, file):
        checker = FileTypeCheckFilter(self.model.__allowed_file_types__)
        try:
            checker.validate_filetype(file)
            return True
        except UnsupportedFileTypeError as exp:
            flash(str(exp))
            return False

    def validate_form(self, form):
        if "uploaded_file" in form:
            file = form["uploaded_file"].data
            if request.endpoint == f"{self.endpoint}.create_view":
                return super().validate_form(form)
            elif request.endpoint == f"{self.endpoint}.edit_view" and not file:
                form["uploaded_file"].data = self.get_one(
                    request.args["id"]
                ).uploaded_file
                form["uploaded_file"].validators = ()
            elif not any(isinstance(file, fs) for fs in (FileStorage, UploadedFile)):
                flash(gettext("Unsupported file type."))
                return False
            elif isinstance(file, FileStorage) and not self.is_valid_file_type(file):
                return False
        return super().validate_form(form)


class ImageAdmin(GenericMediaAdmin):
    list_template = "oy/contrib/media/admin/image_galary.html"

    @expose("/files/<string:file_id>")
    @expose("/thumbnails/<string:size>/<string:file_id>")
    def internal_serve(self, file_id, size=None):
        obj = self.model.query.filter_by(file_id=file_id).one_or_none()
        if obj is None:
            abort(404)
        if size in Image.IMG_SIZES:
            file = self.file_storage.get(obj.get_thumbnail_id("md"))
        else:
            file = obj.uploaded_file.file
        return FileServeApp(storedfile=file, cache_max_age=0)


def register_admin(app, admin):
    admin.add_view(
        ImageAdmin(
            Image,
            db.session,
            name=lazy_gettext("Images"),
            endpoint="image_admin",
            url="media/images/",
            menu_icon_type="fa",
            menu_icon_value="fa-photo",
            menu_order=500,
        )
    )
    admin.add_view(
        GenericMediaAdmin(
            Document,
            db.session,
            name=lazy_gettext("Documents"),
            endpoint="document_admin",
            url="media/documents/",
            menu_icon_type="fa",
            menu_icon_value="fa-file",
            menu_order=400,
        )
    )
