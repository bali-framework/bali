"""
Manager base classes

Sync Manager is usually bind to `io`, like User.io.create
Async Manager is usually bind to `aio`, like User.aio.create

Manager's default methods are aligned to SQLA-Wrapper 4.x
https://github.com/jpsca/sqla-wrapper/blob/v4.200628/sqla_wrapper/default_model.py
"""
import warnings

from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class Base:
    """Manager's Base class"""
    db = None
    model = None

    def __init__(self, instance):
        self.instance = instance


class Manager(Base):
    """Sync Manager is usually bind to `io`"""

    @classmethod
    def exists(cls, **attrs):
        """Returns whether an object with these attributes exists."""
        query = cls.model.query().filter_by(**attrs).exists()
        return bool(cls.db.s.query(query).scalar())

    @classmethod
    def create(cls, **attrs):
        """
        Create and persist a new record for the model, and returns it.
        """
        return cls.model(**attrs).save()

    @classmethod
    def create_or_first(cls, **attrs):
        """Tries to create a new record, and if it fails
        because already exists, return the first it founds."""
        try:
            return cls.create(**attrs)
        except IntegrityError:
            cls.db.s.rollback()
            return cls.first(**attrs)

    @classmethod
    def first(cls, **attrs):
        """Returns the first object found with these attributes."""
        return cls.query().filter_by(**attrs).first()

    @classmethod
    def first_or_error(cls, **attrs):
        """Returns the first object found with these attributes
        or raises a `ValueError` if it doesn't find one."""
        obj = cls.first(**attrs)
        if obj is None:
            raise ValueError
        return obj

    @classmethod
    def query(cls):
        return cls.db.s.query(cls.model)


class AsyncManager(Base):
    """Async model bind to aio"""
    @classmethod
    async def exists(cls, **attrs):
        async with cls.db.async_session() as session:
            stmt = select(cls.model).filter_by(**attrs)
            result = await session.execute(stmt)
            return bool(result.scalars().first())

    @classmethod
    async def create(cls, **attrs):
        return await cls.model(**attrs).aio.save()

    @classmethod
    async def create_or_first(cls, **attrs):
        """Tries to create a new record, and if it fails
        because already exists, return the first it founds."""
        async with cls.db.async_session() as session:
            try:
                return await cls.create(**attrs)
            except IntegrityError:
                session.rollback()
                return await cls.first(**attrs)

    @classmethod
    async def first(cls, **attrs):
        async with cls.db.async_session() as session:
            stmt = select(cls.model).filter_by(**attrs)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def save(self):
        warnings.warn(
            '`Model.aio.save()` is deprecated and will be removed in v3.5, '
            'use instance.save() instead',
            DeprecationWarning,
        )
        async with self.db.async_session() as session:
            session.add(self.instance)
            await session.commit()
            return self.instance

    async def delete(self):
        warnings.warn(
            '`Model.aio.delete()` is deprecated and will be removed in v3.5, '
            'use instance.delete() instead',
            DeprecationWarning,
        )
        async with self.db.async_session() as session:
            session.delete(self.instance)
            await session.commit()
