from typing import Optional

from pydantic import BaseModel

from bali.db.operators import get_filters_expr
from bali.decorators import action
from bali.resource import Resource
from bali.schemas import ListRequest
from models import Item
from permissions import IsAuthenticated
from schemas import ItemModel


class QFilter(BaseModel):
    name: str


class ItemResource(Resource):

    schema = ItemModel
    filters = [
        {
            'name': Optional[str]
        },
    ]
    permission_classes = [IsAuthenticated]

    @action()
    def get(self, pk=None):
        return Item.first(id=pk)

    @action()
    def list(self, schema_in: ListRequest = None):
        return Item.query().filter(*get_filters_expr(Item, **schema_in.filters))

    @action()
    def create(self, schema_in: schema = None):
        return Item.create(**schema_in.dict())

    @action()
    def update(self, schema_in: schema = None, pk=None):
        item = Item.first(id=pk)
        for k, v in schema_in.dict():
            setattr(item, k, v)
        return item.save()

    @action()
    def delete(self, pk=None):
        item = Item.first(id=pk)
        item.delete()
        return {'result': True}

    @action(detail=False)
    def recents(self):
        """List recent 2 record"""
        items = Item.query().limit(2)
        return [self.schema(**item.dict()) for item in items]

    @action(detail=False)
    def recents_q(self, schema_in: QFilter = None):
        """List recent 2 record"""
        print('schema_in', schema_in)
        items = Item.query().limit(2)
        return [self.schema(**item.dict()) for item in items]

    @action(detail=True)
    def items_recents(self, pk=None):
        items = Item.query().filter(Item.id == pk).limit(1)
        return [self.schema(**item.dict()) for item in items]
