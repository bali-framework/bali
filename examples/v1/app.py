import os
import random
import threading
import time

from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from bali.core import APIRouter
from bali.core import db
from models import Item

router = APIRouter()


def echo_container(request_id):
    # return
    print('### <%d> - running container ###' % request_id)
    print('Process id: %s' % os.getpid())
    t = threading.currentThread()
    print('Thread id : %d' % t.ident)
    print('Thread name : %s' % t.getName())
    print('------------------------------\n')


def echo_db_info(request_id):
    # return
    print('### <%d> - running db info ###' % request_id)
    print('db._session', id(db._session))
    print('db._session._session', id(db._session._session))
    print('db._session.engine.pool.status()', db._session.engine.pool.status())
    print('------------------------------\n')


@router.get("/")
async def root():
    request_id = random.randint(100, 999)
    echo_container(request_id)
    echo_db_info(request_id)
    return {"message": "Hello World"}


@router.get("/items")
async def list_items():
    request_id = random.randint(100, 999)
    echo_container(request_id)
    echo_db_info(request_id)
    items = list(Item.query().all())
    db._session._session.remove()
    return items


@router.get("/sync")
def sync_root():
    request_id = random.randint(100, 999)
    echo_container(request_id)
    echo_db_info(request_id)
    return {"message": "Sync Hello World"}


# class ItemModel(BaseModel):
#     id: int
#     name: str

ItemModel = sqlalchemy_to_pydantic(Item)


@router.get("/sync/items", response_model=ItemModel)
def sync_list_items():
    request_id = random.randint(100, 999)
    echo_container(request_id)
    echo_db_info(request_id)
    # item = Item.query().first()
    with db.transaction():
        # time.sleep(10)
        item = Item.create(name='test1')
    return item


@router.get("/sync/slow/items", response_model=ItemModel)
def sync_slow_list_items():
    request_id = random.randint(100, 999)
    echo_container(request_id)
    echo_db_info(request_id)
    # item = Item.query().first()
    with db.transaction():
        time.sleep(30)
        item = Item.create(name='slow')
    return item
