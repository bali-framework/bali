import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
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


db.create_all()


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


class TestModelMethods:
    """
    Instance method calls

    sync: user = User(); user.save()
    async：user = User(async=True); user.save()
    """
    def test_sync_save(self):
        username = 'test_sync_save'
        User(username=username).save()
        user = db.s.query(User).filter(User.username == username).first()
        assert user
        assert user.id
        assert user.username == username

    @pytest.mark.asyncio
    async def test_async_save(self):
        # Create model schema to database
        async with db._async_engine.begin() as conn:
            await conn.run_sync(db.BaseModel.metadata.create_all)

        username = 'test_async_save'
        user = User(username=username, aio=True)
        assert user._is_async

        await user.save()

        async with db.async_session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalars().first()

        assert user
        assert user._is_async
        assert user.id
        assert user.username == username

        # Modified username by instance fetch using Query
        modified_username = 'test_async_save_q'
        user.username = modified_username
        await user.save()
        assert await User.aio.exists(id=user.id, username=modified_username)

    def test_sync_delete(self):
        username = 'test_sync_delete'
        User.io.create(username=username)
        user = db.s.query(User).filter(User.username == username).first()
        assert user
        assert user.id
        assert user.username == username

        user.delete()
        assert not User.io.exists(id=user.id)

    @pytest.mark.asyncio
    async def test_async_delete(self):
        username = 'test_async_delete'
        await User(username=username, aio=True).save()

        async with db.async_session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalars().first()

        assert user
        assert user.id
        assert user.username == username

        await user.delete()
        assert not await User.aio.exists(id=user.id)
