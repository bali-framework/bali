from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from bali.db import db
from bali.db.operators import get_filters_expr
from bali.decorators import action
from bali.resource import ModelResource
from bali.schemas import ListRequest
from permissions import IsAuthenticated

DB_URI = 'sqlite:///:memory:'

db.connect(DB_URI)


class User(db.BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), default='')
    age = Column(Integer)


# generate records
db.create_all()
lucy = User.create(**{
    'username': 'Lucy',
    'age': 13,
})
jack = User.create(**{
    'username': 'Jack',
    'age': 20,
})
groot = User.create(**{
    'username': 'Groot',
    'age': 32,
})


class UserSchema(BaseModel):
    id: int
    username: str
    age: int


class UserResource(ModelResource):
    model = User
    schema = UserSchema
    filters = [
        {'username': str},
        {'age': Optional[str]},
    ]  # yapf: disable
    permission_classes = [IsAuthenticated]

    @action(detail=False)
    def recents(self):
        return User.query().all()[:2]


def test_model_resource_instance():
    resource = UserResource()
    assert hasattr(resource, 'as_router')
    assert resource._is_http
    assert not resource._is_rpc


def test_model_resource_generic_actions():
    resource = UserResource()
    get_result = resource.get(pk=1)
    assert get_result == User.first(id=1)


def test_model_resource_custom_actions():
    resource = UserResource()
    assert len(resource.recents()) > 0
