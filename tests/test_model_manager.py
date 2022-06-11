"""
Test the new model manager API start v3.2.0

Model's Manager usage, replace Model class method

Sync: User.io.exists(pk=1)
Async: User.aio.exists(pk=1)
"""

import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from bali.db import db

DB_URI = 'sqlite:///:memory:'

# Noted that there will be 2 sqlite instance (sync/async)
# because we are using in-memory sqlite
db.connect(DB_URI)

Base = declarative_base()


class User(db.BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(20), index=True)


db.create_all()


class TestSyncManager:
    def test_io_create(self):
        username = 'test_io_create'
        user = User.io.create(username=username)
        assert user

        expect_user = db.s.query(User).filter(User.username == username,
                                             ).first()
        assert user.id == expect_user.id
        assert user.username == expect_user.username

    def test_io_exists(self):
        username = 'test_io_exists'
        user = User(username=username)
        db.s.add(user)
        db.s.commit()

        assert User.io.exists(id=user.id)
        assert User.io.exists(username=username)

    def test_io_not_exists(self):
        assert not User.io.exists(id=0)
        assert not User.io.exists(username='test_io_not_exists')

    def test_io_create_or_first_use_create(self):
        username = 'use_io_create'
        assert not User.io.exists(username=username)

        user = User.io.create_or_first(username=username)
        assert user
        assert user.id > 0

    def test_io_create_or_first_use_first(self):
        username = 'use_io_first'
        expect_user = User.io.create(username=username)
        assert expect_user

        user = User.io.create_or_first(id=expect_user.id, username=username)
        assert user.id == expect_user.id

    def test_io_first(self):
        username = 'test_io_first'
        expect_user = User.io.create(username=username)
        assert expect_user

        user = User.io.first(username=username)
        assert user.id == expect_user.id


@pytest.fixture
async def async_create_all():
    # Create model schema to database
    async with db._async_engine.begin() as conn:
        await conn.run_sync(db.BaseModel.metadata.create_all)


class TestAsyncManager:
    @staticmethod
    async def db_init():
        # Create model schema to database
        async with db._async_engine.begin() as conn:
            await conn.run_sync(db.BaseModel.metadata.create_all)

    @pytest.mark.asyncio
    async def test_aio_create(self, async_create_all):
        await self.db_init()
        username = 'test_aio_create'
        await User.aio.create(username=username)

        async with db.async_session() as session:
            result = await session.execute(
                select(User).where(User.username == username, )
            )
            user = result.scalars().first()

        assert user.id > 0
        assert user.username == username

    @pytest.mark.asyncio
    async def test_aio_exists(self):
        await self.db_init()
        username = 'test_aio_exists'
        async with db.async_session() as session:
            user = User(username=username)
            session.add(user)
            await session.commit()

        assert await User.aio.exists(id=user.id)
        assert await User.aio.exists(username=username)

    @pytest.mark.asyncio
    async def test_aio_not_exists(self):
        await self.db_init()
        assert not await User.aio.exists(id=0)
        assert not await User.aio.exists(username='test_io_not_exists')

    @pytest.mark.asyncio
    async def test_aio_create_or_first_use_create(self):
        await self.db_init()
        username = 'use_aio_create'
        assert not await User.aio.exists(username=username)

        user = await User.aio.create_or_first(username=username)
        assert user
        assert user.id > 0

    @pytest.mark.asyncio
    async def test_aio_create_or_first_use_first(self):
        await self.db_init()
        username = 'use_aio_first'
        expect_user = await User.aio.create(username=username)
        assert expect_user

        user = await User.aio.create_or_first(
            id=expect_user.id, username=username
        )
        assert user.id == expect_user.id

    @pytest.mark.asyncio
    async def test_aio_first(self):
        await self.db_init()
        username = 'test_aio_first'
        expect_user = await User.aio.create(username=username)
        assert expect_user

        user = await User.aio.first(username=username)
        assert user.id == expect_user.id
