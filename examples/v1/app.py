from fastapi_pagination import LimitOffsetPage, LimitOffsetParams, paginate
from fastapi import Query

from bali.core import APIRouter, cache_memoize
from models import Item
from resources import GreeterResource
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

#
# @router.get("/sync")
# def sync_root():
#     request_id = random.randint(100, 999)
#     echo_container(request_id)
#     echo_db_info(request_id)
#     return {"message": "Sync Hello World"}


# @router.get("/sync/items", response_model=ItemModel)
# def sync_list_items():
#     # item = Item.query().first()
#     with db.transaction():
#         # time.sleep(10)
#         item = Item.create(name='test1')
#     return item
#
#
# @router.get("/sync/slow/items", response_model=ItemModel)
# def sync_slow_list_items():
#     # item = Item.query().first()
#     with db.transaction():
#         time.sleep(30)
#         item = Item.create(name='slow')
#     return item
#
#
# @router.get('/greeters/{greeter_id}')
# def get_greeter(greeter_id):
#     pass


# @router.get('/greeters/{greeter_id}')
# def get_greeter(greeter_id):
#     return GreeterResource().get(GetRequest(id=greeter_id))

#
# @router.patch('/greeters/{greeter_id}')
# def get_greeter(greeter_id, body):
#     return GreeterResource.patch(UpdateRequest(id=greeter_id, data=body))

hello_greeter_router = GreeterResource.as_router()
router.include_router(hello_greeter_router, prefix='/hello-greeters')
