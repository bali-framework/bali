from bali import Bali, APIRouter
from fastapi.testclient import TestClient

router = APIRouter()


@router.get("/")
async def read_main():
    return {"msg": "Hello World"}


app = Bali(routers=[{
    "router": router,
    "prefix": "/api",
}], )

client = TestClient(app)


def test_read_main():
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
