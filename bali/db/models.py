"""Model included

`db.BaseModel` is the most common model.
If you don't use `db.BaseModel`, you can compose Mixins to `db.Model`

Import Mixins in your project examples:

    ```python
    from bali.db.models import GenericModelMixin, ManagerMixin
    ```

"""

from contextvars import ContextVar
from datetime import datetime
from typing import List, Dict

import pytz
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import reconstructor
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import func
from sqlalchemy.types import TypeDecorator

from .managers import Manager, AsyncManager
from ..aio.sessions import session_is_async
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


context_auto_commit: ContextVar[bool] = ContextVar(
    'context_auto_commit', default=True
)


def async_method_generate(self, attr):
    """Generate generic async methods"""
    async def save():
        async with self._db.async_session() as session:
            session.add(self)
            await session.commit()
            return self

    async def delete():
        async with self._db.async_session() as session:
            await session.delete(self)
            await session.commit()

    async def dummy():
        raise NotImplementedError("Removed async methods' prefix `async_`")

    methods = {
        'save': save,
        'delete': delete,
        'dummy': dummy,
    }

    return methods.get(attr)


def get_base(db):
    class Base(db.Model, AsyncModelMixin, ManagerMixin):
        __abstract__ = True
        __asdict_include_hybrid_properties__ = False

        # Bind SQLA-wrapper database to model
        _db = db

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

    return Base


def get_base_model(db):
    class BaseModel(
        db.Model, AsyncModelMixin, GenericModelMixin, ManagerMixin
    ):
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


# expose the include models and model creator
# Out of the box base models
included_models = {
    'Base': get_base,
    'BaseModel': get_base_model,
}

# --------------------  Models Mixins  -------------------- #


class AsyncModelMixin:
    """
    Given model async supported

        ```python
        # async instance
        async_instance = Model(async=True)
        ```

    model method starts with prefix `async_`
    will transform to replace a copy replace the prefix

    for example, if you define a model with `async_foo`

        ```python
        class User(db.Base):
            async def foo(self):
                return 'sync result'

            async def async_foo(self):
                return 'async result'

        # call the method of async instance
        # it will return the "async result"
        user = User(async=True):
        assert user.foo() == 'async result'
        ```

    """
    @reconstructor
    def init_on_load(self):
        in_async_context = session_is_async.get()
        return self._as_async() if in_async_context else self

    def _as_async(self):
        """Convert model instance to async model instance

        Here are the things to do:
        1. Bind async generic methods, like `save()`, `delete()`
        2. Removed async methods' prefix `async_`
        """
        self._is_async = True

        self.save = async_method_generate(self, 'save')
        self.delete = async_method_generate(self, 'delete')

        properties = dir(self)
        for method in properties:
            if method.startswith('async_'):
                new_method = method.replace('async_', '', 1)
                setattr(self, new_method, getattr(self, method))
                setattr(self, method, async_method_generate(self, 'dummy'))

        return self


class GenericModelMixin:
    """Generic model include the following fields"""
    created_time = Column(DateTime, default=datetime.utcnow)
    updated_time = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active = Column(Boolean, default=True)


class ManagerMixin:
    """ManagerMixin

    All sync method accessed by `io`
    All async method accessed by `aio`

    Sync examples:
        ```python
        # Sync
        User.io.first()
        # Async
        await User.aio.first()
        ```
    """
    io = Manager
    aio = AsyncManager
