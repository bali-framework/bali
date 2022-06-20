from pydantic import BaseModel

from bali.core import APIRouter, Bali, db, cache, cache_memoize
from bali.db.managers import Manager, AsyncManager
from bali.resources import Resource, ModelResource

__version__ = '3.2.0'


class Schema(BaseModel):
    pass
