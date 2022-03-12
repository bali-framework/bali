"""Model included

`db.BaseModel` is the most common model.
If you don't use `db.BaseModel`, you can compose Mixins to `db.Model`

Import Mixins in your project examples:

    ```python
    from bali.db.models import GenericModelMixin, AsyncModelMixin
    ```

"""

from contextvars import ContextVar
from datetime import datetime
from typing import List, Dict

import pytz
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import func
from sqlalchemy.types import TypeDecorator

from ..utils import timezone


class AwareDateTime(TypeDecorator):
    impl = DateTime

    @property
    def python_type(self):
        return datetime

    def process_result_value(self, value, _):
        if value is not None:
            value = timezone.make_aware(value, timezone=pytz.utc)

        return value

    def process_bind_param(self, value, _):
        if value is not None and timezone.is_aware(value):
            value = timezone.make_naive(value, timezone=pytz.utc)

        return value


context_auto_commit = ContextVar('context_auto_commit', default=True)


def get_base_model(db):
    class BaseModel(db.Model, GenericModelMixin, AsyncModelMixin):
        __abstract__ = True
        __asdict_include_hybrid_properties__ = False

        # Bind SQLA-wrapper database to model
        _db = db

        @classmethod
        def exists(cls, **attrs):
            """Returns whether an object with these attributes exists."""
            query = cls.query().filter_by(**attrs).exists()
            return bool(db.s.query(query).scalar())

        @classmethod
        def create(cls, **attrs):
            """
            Create and persist a new record for the model, and returns it.
            """
            return cls(**attrs).save()

        @classmethod
        def create_or_first(cls, **attrs):
            """Tries to create a new record, and if it fails
            because already exists, return the first it founds."""
            try:
                return cls.create(**attrs)
            except IntegrityError:
                db.s.rollback()
                return cls.first(**attrs)

        @classmethod
        def first(cls, **attrs):
            """Returns the first object found with these attributes."""
            return cls.query().filter_by(**attrs).first()

        @classmethod
        def first_or_error(cls, **attrs):
            """Returns the first object found with these attributes
            or raises a `ValuError` if it doesn't find one."""
            obj = cls.first(**attrs)
            if obj is None:
                raise ValueError
            return obj

        @classmethod
        def query(cls):
            return db.s.query(cls)

        def save(self):
            """Override default model's save"""
            global context_auto_commit
            db.s.add(self)
            db.s.commit() if context_auto_commit.get() else db.s.flush()
            return self

        def delete(self):
            """Override default model's delete"""
            global context_auto_commit
            db.s.delete(self)
            db.s.commit() if context_auto_commit.get() else db.s.flush()

        def _asdict(self, **kwargs):
            include_hybrid_properties = kwargs.setdefault(
                "include_hybrid_properties",
                self.__asdict_include_hybrid_properties__
            )

            output_fields = []
            for i in inspect(type(self)).all_orm_descriptors:
                if isinstance(i, InstrumentedAttribute):
                    output_fields.append(i.key)
                elif isinstance(
                    i, hybrid_property
                ) and include_hybrid_properties:
                    output_fields.append(i.__name__)

            return {i: getattr(self, i, None) for i in output_fields}

        dict = to_dict = _asdict

        @classmethod
        def count(cls, **attrs) -> int:
            return db.s.query(func.count(cls.id)).filter_by(**attrs).scalar()

        @classmethod
        def get_fields(cls) -> List[str]:
            return [c.name for c in cls.__table__.columns]

        @classmethod
        def get_or_create(cls, defaults: Dict = None, **kwargs):
            instance = db.s.query(cls).filter_by(**kwargs).one_or_none()
            if instance:
                return instance, False

            instance = cls(**{**kwargs, **(defaults or {})})  # noqa
            try:
                db.s.add(instance)
                db.s.commit()
                return instance, True
            except SQLAlchemyError:
                db.s.rollback()
                instance = db.s.query(cls).filter_by(**kwargs).one()
                return instance, False

        @classmethod
        def update_or_create(cls, defaults: Dict = None, **kwargs):
            try:
                try:
                    instance = (
                        db.s.query(cls).filter_by(
                            **kwargs
                        ).populate_existing().with_for_update().one()
                    )
                except NoResultFound:
                    instance = cls(**{**kwargs, **(defaults or {})})  # noqa
                    try:
                        db.s.add(instance)
                        db.s.commit()
                    except SQLAlchemyError:
                        db.s.rollback()
                        instance = (
                            db.s.query(cls).filter_by(
                                **kwargs
                            ).populate_existing().with_for_update().one()
                        )
                    else:
                        return instance, True
            except SQLAlchemyError:
                db.s.rollback()
                raise
            else:
                for k, v in defaults.items():
                    setattr(instance, k, v)
                db.s.add(instance)
                db.s.commit()
                db.s.refresh(instance)
                return instance, False

    return BaseModel


class AsyncModelManager:
    """Async model bind to aio"""

    db = None
    model = None

    def __init__(self, instance):
        self.instance = instance

    @classmethod
    async def exists(cls, **attrs):
        async with cls.db.async_session() as async_session:
            stmt = select(cls.model).filter_by(**attrs)
            result = await async_session.execute(stmt)
            return bool(result.scalars().first())

    @classmethod
    async def create(cls, **attrs):
        await cls.model(**attrs).aio.save()

    @classmethod
    async def first(cls, **attrs):
        async with cls.db.async_session() as async_session:
            stmt = select(cls.model).filter_by(**attrs)
            result = await async_session.execute(stmt)
            return result.scalars().first()

    async def save(self):
        async with self.db.async_session() as async_session:
            async_session.add(self.instance)
            await async_session.commit()
            return self.instance

    async def delete(self):
        async with self.db.async_session() as async_session:
            async_session.delete(self.instance)
            await async_session.commit()


# expose the include models and model creator
included_models = {
    'BaseModel': get_base_model,
}

# --------------------  Models Mixins  -------------------- #


class GenericModelMixin:
    """Generic model include the following fields"""
    created_time = Column(DateTime, default=datetime.utcnow)
    updated_time = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active = Column(Boolean, default=True)


class AsyncModelMixin:
    """Async models methods

    All async method accessed by `aio`

        ```python
        # Model
        async def get_first_user()
            await User.aio.first()

        # Instance
        user = User()
        user.aio.save()
        ```

    """

    aio = AsyncModelManager
