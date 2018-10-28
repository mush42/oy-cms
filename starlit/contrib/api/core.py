import json
from six import with_metaclass
from flask import request, abort as flask_abort
from flask.views import MethodViewType
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import URLFor
from flask_marshmallow.sqla import SchemaOpts
from flask_cors import CORS
from inflect import engine
from starlit.boot.exts.sqla import db


api = Api(prefix="/api")
ma = Marshmallow()
cors = CORS(resources="/api/*")


class StarlitResourceType(MethodViewType):
    """Provides automatic endpoint registration for  collection and resource views."""

    @staticmethod
    def gen_default_api_endpoints(cls):
        e = engine()
        model_name = cls.schema.Meta.model.__name__.lower()
        identifier = e.plural(model_name)
        rv = {
            "/%s/"
            % identifier: {
                "endpoint": "%s-collection" % model_name,
                "methods": ["GET", "POST"],
            },
            "/%s/<int:pk>/"
            % identifier: {
                "endpoint": "%s-resource" % model_name,
                "methods": ["GET", "PUT", "DELETE"],
            },
        }
        return rv

    def __new__(cls, name, bases, d):
        rv = MethodViewType.__new__(cls, name, bases, d)
        if not rv.schema:
            return rv
        default_endpoints = cls.gen_default_api_endpoints(rv)
        if hasattr(rv, "url_map"):
            default_endpoints.update(rv.url_map)
        for url, options in default_endpoints.items():
            api.add_resource(
                rv,
                url,
                methods=options.get("methods", ["POST", "PUT", "DELETE", "GET"]),
                endpoint=options.get("endpoint"),
            )
        site_endpoint = getattr(rv.schema, "site_endpoint", [])
        if site_endpoint:
            rv.schema._declared_fields["site_url"] = URLFor(
                site_endpoint[0], **site_endpoint[1]
            )
        return rv


class StarlitResource(with_metaclass(StarlitResourceType, Resource)):
    """
    A Base API resource that provides basic CRUD oparations for sub-classes.
    It also register all subclasses with the api.
    To use it provide a sqlalchemy-marshmallow schema.
    """

    schema = None

    def schema_dump(self, obj, schema_kwargs=None, **kwargs):
        options = getattr(self.schema, "dump_options", {})
        kw = options.get("one" if not kwargs.get("many") else "many", {})
        kw.update(schema_kwargs or {})
        mod_schema = self.schema(**kw)
        return mod_schema.dump(obj, **kwargs)

    def query_one(self, pk):
        """
        Returns an object or None
        Subclasses may overide this method to implement custom database query logic.
        """
        return self.schema.Meta.model.query.get(pk)

    def query_all(self):
        """
        Returns a queryset
        Subclasses may overide this method to implement custom database query logic.
        This method should return a sqlalchemy query object to enable
        automatic pagination.
        """
        return self.schema.Meta.model.query

    def get(self, pk=None, attr=None):
        if pk:
            obj = self.query_one(pk)
            self.abort(obj)
            return self.schema_dump(obj).data
        page = int(request.args.get("page", 1))
        item_count = int(request.args.get("item_count", 10))
        paginator = self.query_all().paginate(page, item_count, False)
        return (
            self.schema_dump(paginator.items, many=True),
            200,
            {"X-Total-Count": self.query.count},
        )

    def post(self):
        obj, errors = self.schema().load(self.get_post_data())
        if errors:
            return errors, 400
        db.session.add(obj)
        db.session.commit()
        return self.schema_dump(obj).data

    def put(self, pk):
        obj = self.query_one(pk)
        self.abort(obj)
        data, errors = self.schema().load(
            data=self.get_post_data(), instance=obj, partial=True
        )
        if errors:
            return errors, 400
        db.session.add(data)
        db.session.commit()
        return self.schema_dump(obj).data

    def delete(self, pk):
        obj = self.query_one(pk)
        self.abort(obj)
        db.session.delete(obj)
        db.session.commit()
        return {"message": "Resource was deleted successfully"}

    def get_post_data(self):
        _json = request.get_json()
        if _json is None:
            return request.form
        return _json

    def abort(self, obj, status_code=404, message="Resource was not found"):
        if obj is None:
            flask_abort(status_code, message)


class StarlitSchemaOpts(SchemaOpts):
    def __init__(self, meta):
        super(StarlitSchemaOpts, self).__init__(meta)
        self.json_module = json


class StarlitModelSchema(ma.ModelSchema):
    OPTIONS_CLASS = StarlitSchemaOpts


def initialize_api(app):
    api.init_app(app)
    ma.init_app(app)
    cors.init_app(app)
