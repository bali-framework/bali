from fastapi import FastAPI

from bali import Bali, Resource, Schema
from bali.decorators import action


class TestBaliApp:
    def test_initialize_default_values(self):
        app = Bali()
        assert app.base_settings == {}
        assert app.kwargs == {}
        assert isinstance(app._app, FastAPI)

    def test_register(self):
        class TestSchema(Schema):
            content: str

        class TestResource(Resource):
            schema = TestSchema

            @action()
            def get(self, pk=None):
                return {'content': f'hello, ID is {pk}'}


        app = Bali()
        init_routes_count = len(app._app.routes)

        app.register(TestResource)

        assert len(app._app.routes) == init_routes_count + 1

