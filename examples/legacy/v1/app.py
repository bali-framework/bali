from fastapi_pagination import LimitOffsetPage, paginate

from bali.core import APIRouter, cache_memoize
from models import Item
from resources import (
    GreeterResource,
    AsyncGreeterResource,
    ItemResource,
    ItemModelResource,
)
from schemas import ItemModel

router = APIRouter()


@cache_memoize(10)
def get_cacheable_items():
    items = list(Item.query().all())
    print('load from db')
    return items


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/items", response_model=LimitOffsetPage[ItemModel])
def list_items():
    return paginate(get_cacheable_items())


hello_greeter_router = GreeterResource.as_router()
item_router = ItemResource.as_router()
item_model_resource_router = ItemModelResource.as_router()
router.include_router(hello_greeter_router, prefix='/greeters')
router.include_router(
    AsyncGreeterResource.as_router(), prefix='/async-greeters'
)
router.include_router(item_router, prefix='/items')
router.include_router(item_model_resource_router, prefix='/models-items')
