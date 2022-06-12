"""
Bali ModelResource
"""

from .resource import Resource
from ..db.operators import get_filters_expr
from ..decorators import action
from ..schemas import ListRequest

__all__ = ['ModelResource']


class ModelResource(Resource):
    """
    `ModelResource` is a fast way to implement resource layer
    for model objects
    """
    model = None
    schema = None

    @action()
    def list(self, schema_in: ListRequest = None):
        return self.model.io.query().filter(
            *get_filters_expr(self.model, **schema_in.filters)
        )

    @action()
    def get(self, pk=None):
        return self.model.io.first(id=pk)

    @action()
    def create(self, schema_in: schema = None):
        # noinspection PyUnresolvedReferences
        return self.model.io.create(**schema_in.dict())

    @action()
    def update(self, schema_in: schema = None, pk=None):
        item = self.model.io.first(id=pk)
        # noinspection PyUnresolvedReferences
        for k, v in schema_in.dict().items():
            if v is None:
                continue
            setattr(item, k, v)
        return item.save()

    @action()
    def delete(self, pk=None):
        item = self.model.io.first(id=pk)
        item.delete()
        return {'id': pk, 'result': True}
