from sqlalchemy import Column, Integer

from bali.db import db
from bali.schema import model_to_schema

DB_URI = 'sqlite:///:memory:'


def test_model_to_schema():
    db.connect(DB_URI)

    class User(db.BaseModel):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)

    db.create_all()

    # noinspection PyPep8Naming
    UserSchema = model_to_schema(User)

    user_schema = UserSchema(id=1)
    assert user_schema.id == 1


# noinspection PyUnresolvedReferences
def test_model_to_schema_from_orm():
    db.connect(DB_URI)

    class User(db.BaseModel):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)

    db.create_all()
    user = User.create()
    # noinspection PyPep8Naming
    UserSchema = model_to_schema(User)

    user_schema = UserSchema.from_orm(user)
    assert user_schema.id == 1
    assert user_schema.created_time <= user_schema.updated_time
    assert user_schema.is_active

    expected = {
        'id': user.id,
        'created_time': user.created_time,
        'updated_time': user.updated_time,
        'is_active': user.is_active,
    }

    assert user_schema.dict() == expected, 'Schema to dict value should equal origin model'


