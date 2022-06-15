from pydantic import BaseModel
from typing import List, Optional

from bali.decorators import action
from bali.resources import Resource
from bali.schemas import GetRequest, ListRequest
from ..permissions import IsAuthenticated

GREETERS = [{'id': i, 'content': 'Hi, number %s' % i} for i in range(10)]


class AsyncGreeter(BaseModel):
    id: int
    content: str


class AsyncGreeterFilter(BaseModel):
    ids: List[int]


class AsyncGreeterResource(Resource):

    schema = AsyncGreeter
    filters = [
        {'name': str},
        {'title': Optional[str]},
    ]
    permission_classes = [IsAuthenticated]

    @action(http_only=True)
    async def get(self, pk=None):
        return [g for g in GREETERS if g.get('id') == pk][0]

    @action()
    async def list(self, schema_in: ListRequest = None):
        # `list` NOT FULL SUPPORT HTTP REQUEST
        # return GREETERS[:schema_in.limit]
        print(schema_in.filters.get('name'))
        return GREETERS

    @action()
    async def create(self, schema_in: schema = None):
        return {'id': schema_in.id, 'content': schema_in.content}

    @action()
    async def update(self, schema_in: schema = None, pk=None):
        return {'id': pk, 'content': schema_in.content}

    @action()
    async def delete(self, pk=None):
        return {'result': True}

    @action(detail=False)
    async def recents(self):
        return GREETERS[:2]

    @action(detail=True)
    async def items_recents(self, pk=None):
        return [g for g in GREETERS if g.get('id') == pk]

    @action(detail=False, methods=['post'])
    async def custom_create(self, schema_in: AsyncGreeterFilter):
        print('schema_in', schema_in)
        return GREETERS[0]
