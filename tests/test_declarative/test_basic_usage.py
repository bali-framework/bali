from bali import Bali, APIRouter
from fastapi.testclient import TestClient
from bali.declarative import *


class GreeterInMemorySchema(API.schema):
    id: int
    content: str


class TestDeclarativeBasicUsage:
    def test_greeter(self):
        Bali.__clear__()
        response = {"Hello": "World"}
        API("Greeter").get(response)

        app = Bali()
        client = TestClient(app)
        endpoint = "/greeters"
        response = client.get(f"{endpoint}/1")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    def test_greeter_multi_actions(self):
        Bali.__clear__()
        response = {"Hello": "World"}
        API("GreeterMultiAction").list([response, response]).get(response)

        app = Bali()
        client = TestClient(app)
        endpoint = "/greeter-multi-actions"
        response = client.get(f"{endpoint}")
        assert response.status_code == 200
        assert response.json() == {
            "items": [{
                "Hello": "World"
            }, {
                "Hello": "World"
            }],
            "limit": 50,
            "offset": 0,
            "total": 2,
        }

        response = client.get("/greeters/1")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    def test_greeter_in_memory_storage(self):
        Bali.__clear__()
        API("GreeterMemoryStorage").schema(GreeterInMemorySchema).all()

        app = Bali()
        client = TestClient(app)
        endpoint = "/greeter-memory-storages"
        response = client.get(f"{endpoint}")
        assert response.status_code == 200
        assert response.json() == {
            "items": [],
            "limit": 50,
            "offset": 0,
            "total": 0,
        }

        GreeterInMemorySchema.push(id=1, content='test')

        response = client.get(f"{endpoint}/1")
        assert response.status_code == 200
        assert response.json() == {'content': 'test', 'id': 1}

