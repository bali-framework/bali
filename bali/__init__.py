from pydantic import BaseModel

from bali.core import Bali, db, cache, cache_memoize
from bali.resources import Resource, ModelResource

__version__ = '3.2.0'


class Schema(BaseModel):
    pass
