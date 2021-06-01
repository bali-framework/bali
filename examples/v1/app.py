from fastapi_pagination import LimitOffsetPage, LimitOffsetParams, paginate
from fastapi import Query

from bali.core import APIRouter, cache_memoize
from models import Item
from resources import GreeterResource, ItemResource
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
router.include_router(hello_greeter_router, prefix='/hello-greeters')
router.include_router(item_router, prefix='/hello-items')
