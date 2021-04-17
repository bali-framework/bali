from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models import Item


class ItemModel(BaseModel):
    id: int
    name: str


ItemModel = sqlalchemy_to_pydantic(Item)
