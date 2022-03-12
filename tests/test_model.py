import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from bali.db import db

DB_URI = 'sqlite:///:memory:'

db.connect(DB_URI)

Base = declarative_base()


class User(db.BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(20), index=True)


class Book(db.BaseModel):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(20), index=True)


@pytest.mark.asyncio
async def test_db_async_model_exists():
    # Create model schema to database
    async with db._async_engine.begin() as conn:
        await conn.run_sync(db.BaseModel.metadata.create_all)

    username = 'Lorry'
    non_username = 'Noname'
    title = 'Design Pattern'

    async with db.async_session() as async_session:
        user = User(username=username)
        book = Book(title=title)
        async_session.add(user)
        async_session.add(book)
        await async_session.commit()

    is_exists = await User.aio.exists(username=username)
    assert isinstance(is_exists, bool)
    assert is_exists, f'{username} should exists'

    is_exists = await Book.aio.exists(title=title)
    assert isinstance(is_exists, bool)
    assert is_exists, f'Book {title} should exists'

    is_exists = await User.aio.exists(username=non_username)
    assert isinstance(is_exists, bool)
    assert not is_exists, f'{non_username} should not exists'


@pytest.mark.asyncio
async def test_db_async_instance_save():
    # Create model schema to database
    async with db._async_engine.begin() as conn:
        await conn.run_sync(db.BaseModel.metadata.create_all)

    username = 'Jeff Inno'
    user = User(username=username)
    await user.aio.save()

    is_exists = await User.aio.exists(username=username)
    assert isinstance(is_exists, bool)
    assert is_exists, 'User should persisted into database'
