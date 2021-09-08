"""
Bali ModelResource
"""

from .resource import Resource
from ..db.operators import get_filters_expr
from ..schemas import ListRequest

__all__ = ['ModelResource']


class ModelResource(Resource):
    """
    `ModelResource` is a fast way to implement resource layer
    for model objects
    """
    model = None
    schema = None

    def list(self, schema_in: ListRequest = None):
        return self.model.query().filter(
            *get_filters_expr(self.model, **schema_in.filters)
        )

    def get(self, pk=None):
        return self.model.first(id=pk)

    def create(self, schema_in: schema = None):
        # noinspection PyUnresolvedReferences
        return self.model.create(**schema_in.dict())

    def update(self, schema_in: schema = None, pk=None):
        item = self.model.first(id=pk)
        # noinspection PyUnresolvedReferences
        for k, v in schema_in.dict():
            setattr(item, k, v)
        return item.save()

    def delete(self, pk=None):
        item = self.model.first(id=pk)
        item.delete()
        return {'id': pk, 'result': True}
