import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from bali.db import db

DB_URI = 'sqlite:///:memory:'

db.connect(DB_URI)

Base = declarative_base()



class User(db.BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)


db.create_all()


def test_db_connect():
    assert db._db is not None
    assert db._async_engine is not None
    assert isinstance(db.async_session, sessionmaker)


def test_base_model():
    # using the exists columns
    users = db.s.query(User.created_time, User.updated_time,
                       User.is_active).all()
    assert len(users) >= 0


def test_base_model_create_entity():
    user = User.create()
    assert user.id > 0  # create successfully
    assert user.created_time <= user.updated_time
    assert user.is_active


@pytest.mark.asyncio
async def test_base_model_create_entity_async():
    # Create model schema to database
    async with db._async_engine.begin() as conn:
        await conn.run_sync(db.BaseModel.metadata.create_all)

    async with db.async_session() as async_session:
        user = User()
        async_session.add(user)
        await async_session.commit()

    assert user.id > 0  # create successfully
    assert user.created_time <= user.updated_time
    assert user.is_active
