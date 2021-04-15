from pydantic import BaseModel
from bali.decorators import action
from bali.resource import Resource
from bali.schemas import GetRequest, ListRequest

GREETERS = [{'id': i, 'content': 'Hi, number %s' % i} for i in range(10)]


class Greeter(BaseModel):
    id: int
    content: str


class GreeterResource(Resource):

    schema = Greeter

    def get(self, pk=None):
        return [g for g in GREETERS if g.get('id') == pk][0]

    def list(self, schema_in: ListRequest):
        return GREETERS[:schema_in.limit]

    def create(self, schema_in: schema):
        return {'id': schema_in.id, 'content': schema_in.content}

    def update(self, schema_in: schema, pk=None):
        return {'id': pk, 'content': schema_in.content}

    def delete(self, pk=None):
        return {'result': True}

    @action(detail=False)
    def recents(self, schema_in):
        return GREETERS[:2]
