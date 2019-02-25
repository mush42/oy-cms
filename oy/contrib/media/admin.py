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
from flask import current_app, Blueprint, flash, request, abort, url_for, redirect
from flask_admin import expose
from flask_admin.model.template import EndpointLinkRowAction
from oy.babel import gettext, lazy_gettext
from oy.models import db
from oy.contrib.admin import OyModelView
from oy.contrib.admin.fields import BootstrapFileInputField, TagsField
from .models import Image, Document
from .serving import ModelFileServer
from .utils import FileTypeCheckFilter, UnsupportedFileTypeError


class FileDownloadRowAction(EndpointLinkRowAction):
    def render(self, context, row_id, row):
        row_id = row.file_id
        return super().render(context, row_id, row)


class GenericMediaAdmin(OyModelView):
    list_template = "oy/contrib/media/admin/list.html"
    form_columns = ["title", "tags", "uploaded_file", "description"]
    form_extra_fields = dict(tags=TagsField(label=lazy_gettext("Tags")))
    form_overrides = dict(uploaded_file=BootstrapFileInputField)
    form_widget_args = dict(uploaded_file=dict(required=False))
    column_list = ["title", "created"]
    column_searchable_list = ["tags", "title", "description"]
    column_extra_row_actions = [
        FileDownloadRowAction(
            "fa fa-download",
            ".serve_file_with_id",
            title=lazy_gettext("Download"),
            id_arg="file_id",
        )
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fileserver = ModelFileServer(model=self.model)

    def create_blueprint(self, admin):
        blueprint = super().create_blueprint(admin)
        # A blueprint to serve files for media admin
        if "oy.contrib.media.admin" not in current_app.blueprints:
            current_app.register_blueprint(
                Blueprint(
                    name="oy.contrib.media.admin",
                    import_name="oy.contrib.media.admin",
                    static_folder="static",
                    template_folder="templates",
                    static_url_path="/static/admin/media",
                )
            )
        blueprint.register_error_handler(
            UnsupportedFileTypeError, self.handle_unsupported_file_types
        )
        return blueprint

    def search_placeholder(self):
        return gettext("Search")

    def handle_unsupported_file_types(self, error):
        flash(gettext(f"Error uploading file. {error}"))
        return redirect(request.path)

    @expose("/download/<file_id>")
    def serve_file_with_id(self, file_id):
        doc = self.model.query.filter_by(file_id=file_id).one()
        return self.fileserver(doc.file_id)

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
            file = obj.uploaded_file.get_thumbnail("sm")
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
