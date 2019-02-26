from urllib.parse import urlparse, parse_qs
from flask import redirect, request, url_for, abort
from flask_admin import expose
from flask_admin.model.template import (
    EndpointLinkRowAction,
    TemplateLinkRowAction,
    EditRowAction,
    LinkRowAction,
)
from flask_admin.helpers import validate_form_on_submit
from wtforms.fields import HiddenField
from wtforms_components.fields import SelectField
from wtforms.validators import ValidationError, InputRequired
from oy.boot.sqla import db
from oy.babel import gettext, lazy_gettext
from oy.models.page import Page
from .displayable_admin import DisplayableAdmin, DISPLAYABEL_DEFAULTS


class PageAdmin(DisplayableAdmin):
    list_template = "admin/oy/page/list.html"
    form_columns = list(DISPLAYABEL_DEFAULTS["form_columns"])
    form_columns.insert(0, "title")
    form_columns.insert(4, "parent")
    form_columns.insert(5, "slug")
    form_excluded_columns = DISPLAYABEL_DEFAULTS["form_excluded_columns"] + []
    column_list = ["title", "status", "updated"]
    column_editable_list = ["title"]
    column_default_sort = ("tree_id", False)

    # A lookup dict mapping table names to admin_view endpoints
    _tablename_to_endpoint = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tablename_to_endpoint.setdefault(
            self.model.__tablename__, (self.endpoint, self.name)
        )

    def _get_parent_from_args(self):
        parent_pk = request.args.get("parent_pk")
        if not parent_pk:
            return
        parent = self.get_one(parent_pk)
        if not parent:
            abort(404)
        else:
            return parent

    def get_query(self):
        parent = self._get_parent_from_args()
        if parent:
            return db.session.query(Page).filter(Page.parent == parent)
        return self.model.query.roots

    def get_count_query(self):
        parent = self._get_parent_from_args()
        sel = db.select([db.func.count(Page.id)])
        if parent:
            sel = sel.where(Page.parent == parent)
        else:
            sel = sel.where(
                db.and_(
                    Page.parent == None,
                    db.inspect(Page).polymorphic_on
                    == db.inspect(self.model).polymorphic_identity,
                )
            )
        return db.session.execute(sel)

    def create_form(self, obj=None):
        form = super().create_form(obj)
        parent = self._get_parent_from_args()
        if parent is None and request.args.get("url"):
            qs = parse_qs(urlparse(request.args["url"]).query)
            if "parend_pk" in qs:
                parent = self.get_one(qs["parent_pk"])
        if parent:
            form.parent.data = parent
        return form

    def get_list_row_actions(self):
        actions = super().get_list_row_actions()
        if self.can_edit:
            actions = [a for a in actions if not isinstance(a, EditRowAction)]
            actions.insert(
                0,
                LinkRowAction(
                    "fa fa-pencil",
                    url=self._get_edit_view_endpoint,
                    title=lazy_gettext("Edit record"),
                ),
            )
        actions.extend(
            [
                TemplateLinkRowAction(
                    template_name="oy.add_child_row_action",
                    title=lazy_gettext("Add child"),
                ),
                TemplateLinkRowAction(
                    template_name="oy.children_row_action",
                    title=gettext("Show children"),
                ),
            ]
        )
        return actions

    def _get_edit_view_endpoint(self, act, row_id, row):
        args = {"id": row_id, "url": self.get_save_return_url(row)}
        endpoint = self._tablename_to_endpoint[row.__tablename__][0]
        return url_for(f"{endpoint}.edit_view", **args)

    def init_actions(self):
        self._actions = []
        self._actions_data = {}

    def edit_form(self, obj):
        form = super().edit_form(obj)
        form.parent.query_factory = lambda: Page.query.filter(Page.id != obj.id)
        return form

    def get_child_page_type_form(self):
        class ChildPageTypeForm(self.form_base_class):
            parent_pk = HiddenField(validators=[InputRequired()])
            url = HiddenField()
            page_type = SelectField(
                validators=[InputRequired()],
                label=lazy_gettext("Child page type"),
                choices=lambda: (
                    (k, v.title()) for (k, v) in self._tablename_to_endpoint.values()
                ),
            )

        return ChildPageTypeForm()

    def get_preview_url(self, instance):
        return f"/{instance.url}/"

    @expose("/create-redirector", methods=("POST",))
    def create_redirector(self):
        form = self.get_child_page_type_form()
        if validate_form_on_submit(form):
            endpoint = self._tablename_to_endpoint[form.page_type.data][0]
            return redirect(
                url_for(
                    f"{endpoint}.create_view",
                    parent_pk=form.parent_pk.data,
                    url=form.url.data,
                )
            )
