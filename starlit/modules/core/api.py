from marshmallow import fields
from starlit.boot.exts.api import StarlitModelSchema, StarlitResource
from starlit.models.abstract import Displayable
from starlit.modules.core.models import Site

class SiteSchema(StarlitModelSchema):
    class Meta:
        model = Site


class SiteResource(StarlitResource):
    schema = SiteSchema

class DisplayableSchema(StarlitModelSchema):
    site = fields.Nested(SiteSchema, only=['id', 'name', 'is_active'])


class DisplayableResource(StarlitResource):
    schema = None
    
    def query_one(self, pk):
        return self.schema.Meta.model.query.get(pk)
    
    def query_all(self):
        return self.schema.Meta.model.query.published

