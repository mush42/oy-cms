from marshmallow import fields
from oy.boot.exts.api import OyModelSchema, OyResource
from oy.models.abstract import Displayable
from oy.modules.core.models import Site


class SiteSchema(OyModelSchema):
    class Meta:
        model = Site


class SiteResource(OyResource):
    schema = SiteSchema


class DisplayableSchema(OyModelSchema):
    site = fields.Nested(SiteSchema, only=["id", "name", "is_active"])


class DisplayableResource(OyResource):
    schema = None

    def query_one(self, pk):
        return self.schema.Meta.model.query.get(pk)

    def query_all(self):
        return self.schema.Meta.model.query.published
