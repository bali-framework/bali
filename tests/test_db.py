from sqlalchemy import Column, Integer

from bali.db import db

DB_URI = 'sqlite:///:memory:'


# noinspection PyProtectedMember
def test_db_connect():
    db.connect(DB_URI)
    assert db._session is not None


def test_base_model():
    db.connect(DB_URI)

    class User(db.BaseModel):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)

    db.create_all()

    # using the exists columns
    users = db.query(User.created_time, User.updated_time, User.is_active).all()
    assert users == []


def test_base_model_create_entity():
    db.connect(DB_URI)

    class User(db.BaseModel):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)

    db.create_all()
    user = User.create()
    assert user.id > 0  # create successfully
    assert user.created_time <= user.updated_time
    assert user.is_active
