from typing import Optional

from pydantic import BaseModel

from bali.resources import ModelResource
from models import Item
from permissions import IsAuthenticated
from schemas import ItemModel


class QFilter(BaseModel):
    name: str


class ItemModelResource(ModelResource):
    model = Item
    schema = ItemModel
    permission_classes = [IsAuthenticated]
