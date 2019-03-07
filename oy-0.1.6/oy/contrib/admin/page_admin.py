from wtforms.fields import HiddenField
from wtforms_components.fields import SelectField
from wtforms.validators import ValidationError, InputRequired
from flask import current_app, g, flash, redirect, request, url_for, abort
from flask.helpers import locked_cached_property
from flask_admin import expose
from flask_admin.model.template import (
    macro,
    EndpointLinkRowAction,
    TemplateLinkRowAction,
    EditRowAction,
    LinkRowAction,
)
from flask_admin.helpers import (
    is_safe_url,
    validate_form_on_submit,
    get_redirect_target,
)
from flask_wtf import FlaskForm
from oy.boot.sqla import db
from oy.babel import gettext, lazy_gettext
from oy.models.page import Page
from oy.helpers import _missing
from .wrappers import OyDeleteRowAction
from .displayable_admin import DisplayableAdmin, DISPLAYABEL_DEFAULTS


def _ptype_formatter(view, context, model, name):
    ptype = getattr(model, name)
    return view._tablename_to_endpoint[ptype][1].title()


class PageAdmin(DisplayableAdmin):
    list_template = "admin/oy/page/list.html"
    form_columns = list(DISPLAYABEL_DEFAULTS["form_columns"])
    form_columns.insert(0, "title")
    form_columns.insert(4, "slug")
    form_excluded_columns = DISPLAYABEL_DEFAULTS["form_excluded_columns"] + []
    column_list = ["title", "contenttype", "status", "updated"]
    column_editable_list = ["title"]
    column_default_sort = ("tree_id", False)

    # A lookup dict mapping table names to admin_view endpoints
    _tablename_to_endpoint = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tablename_to_endpoint.setdefault(
            self.model.__contenttype__, (self.endpoint, self.name)
        )

    def init_actions(self):
        """Disable bulk actions for pages."""
        self._actions = []
        self._actions_data = {}

    @property
    def column_formatters(self):
        default = super().column_formatters
        default["contenttype"] = _ptype_formatter
        return default

    def _get_parent_from_args(self):
        """Extract a possible parent from a key in the
       request.args called `parent_pk`.
       """
        args_parent = getattr(g, "__args_parent", _missing)
        if args_parent is not _missing:
            return g.__args_parent
        parent_pk = request.args.get("parent_pk")
        if not parent_pk:
            g.__args_parent = None
            return
        parent = Page.query.filter(Page.id == int(parent_pk)).one_or_none()
        if parent:
            g.__args_parent = parent
            return parent
        return abort(404)

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

    @property
    def can_create(self):
        rv = super().can_create
        parent = self._get_parent_from_args()
        if rv and (request.endpoint == f"{self.endpoint}.index_view") and parent:
            return False
        elif parent and not self.model.is_valid_parent(parent):
            if current_app.debug and request.endpoint == f"{self.endpoint}.create_view":
                flash(gettext("Not a valid parent page type."))
            return False
        return rv

    def _handle_view(self, name, **kwargs):
        """Do not show a list for creation and editing only views."""
        if name == "index_view" and not self.show_in_menu:
            return redirect(url_for("admin.index"))
        return super()._handle_view(name, **kwargs)

    def get_form(self):
        form = super().get_form()
        form.parent_id = HiddenField()
        return form

    def create_form(self, obj=None):
        form = super().create_form(obj)
        parent = self._get_parent_from_args()
        if parent and not parent.should_allow_children():
            return abort(404)
        if self.model.should_allow_parents() and parent:
            form.parent_id.data = parent.id
        else:
            del form.parent_id
        return form

    def edit_form(self, obj):
        form = super().edit_form(obj)
        if self.model.should_allow_parents() and obj.parent:
            form.parent_id = obj.id
        else:
            del form.parent_id
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
        if self.can_delete:
            actions = [a for a in actions if not isinstance(a, OyDeleteRowAction)]
            actions.insert(
                0,
                LinkRowAction(
                    "fa fa-trash",
                    url=self._get_delete_endpoint,
                    title=lazy_gettext("Delete record"),
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

    def validate_form(self, form):
        rv = super().validate_form(form)
        if rv and ("parent_id" in form) and form.parent_id.data:
            page = Page.query.get_or_404(form.parent_id.data)
            if not self.model.is_valid_parent(page):
                return False
        return rv

    def _get_edit_view_endpoint(self, act, row_id, row):
        args = {"id": row_id, "url": self.get_save_return_url(row)}
        endpoint = self._tablename_to_endpoint[row.contenttype][0]
        return url_for(f"{endpoint}.edit_view", **args)

    def _get_delete_endpoint(self, act, row_id, row):
        args = {"pk": row_id, "url": self.get_save_return_url(row)}
        endpoint = self._tablename_to_endpoint[row.contenttype][0]
        return url_for(f"{endpoint}.delete_confirm", **args)

    def get_child_page_type_form(self):
        """The form used in the popup when creating a child page."""

        class ChildPageTypeForm(FlaskForm):
            parent_pk = HiddenField(validators=[InputRequired()])
            url = HiddenField(default=self.get_save_return_url(self.model))
            page_type = SelectField(
                validators=[InputRequired()],
                label=lazy_gettext("Select the type of the child page "),
                default="",
                choices=self._get_pchild_form_choices,
            )

        return ChildPageTypeForm()

    @expose("/redirect/new", methods=("POST",))
    def create_redirector(self):
        """Redirect to the appropriate create_view endpoint
        base on the value of `page_type` field in the form
        """
        form = self.get_child_page_type_form()
        url = form.url.data if is_safe_url(form.url.data) else url_for(".index_view")
        if form.validate_on_submit():
            return redirect(
                url_for(
                    f"{form.page_type.data}.create_view",
                    parent_pk=form.parent_pk.data,
                    url=url,
                )
            )
        else:
            return redirect(url)

    @locked_cached_property
    def page_type_map(self):
        """Used in the list template to output a JSON objects
       of page types and their parent and subpage types.
       """
        rv = dict()
        for entity in (m.class_ for m in Page.__mapper__.polymorphic_iterator()):
            contype = entity.__contenttype__
            if contype not in self._tablename_to_endpoint:
                continue
            rv[contype] = []
            valid_children = entity.valid_child_node_types
            if valid_children == self.model.ALL_NODE_TYPES:
                for k, v in self._tablename_to_endpoint.items():
                    rv[contype].append({"endpoint": v[0], "title": v[1].title()})
                continue
            for child in valid_children:
                if child.__contenttype__ in self._tablename_to_endpoint:
                    data = self._tablename_to_endpoint[child.__contenttype__]
                    rv[contype].append({"endpoint": data[0], "title": data[1].title()})
        return rv

    def _get_pchild_form_choices(self):
        if request.endpoint.endswith(".create_redirector"):
            ptype = self.get_child_page_type_form().page_type.data
            for val in self._tablename_to_endpoint.values():
                if ptype == val[0]:
                    return [(ptype, "")]
        return []

    def get_preview_url(self, instance):
        return f"/{instance.url}/"
