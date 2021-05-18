from contextvars import ContextVar
from datetime import datetime
from typing import List

import pytz
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.exc import IntegrityError
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

    def process_bind_param(self, value, dialect):
        if value is not None and timezone.is_aware(value):
            value = timezone.make_naive(value, timezone=pytz.utc)

        return value


context_auto_commit = ContextVar('context_auto_commit', default=True)


def get_base_model(db):
    class BaseModel(db.Model):
        __abstract__ = True

        created_time = Column(DateTime, default=datetime.utcnow)
        updated_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_active = Column(Boolean, default=True)

        @classmethod
        def exists(cls, **attrs):
            """Returns whether an object with these attributes exists."""
            equery = cls.query().filter_by(**attrs).exists()
            return bool(db.session.query(equery).scalar())

        @classmethod
        def create(cls, **attrs):
            """Create and persist a new record for the model, and returns it."""
            return cls(**attrs).save()

        @classmethod
        def create_or_first(cls, **attrs):
            """Tries to create a new record, and if it fails
            because already exists, return the first it founds."""
            try:
                return cls.create(**attrs)
            except IntegrityError:
                db.session.rollback()
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
            return db.session.query(cls)

        def save(self):
            """Override default model's save"""
            global context_auto_commit
            db.session.add(self)
            db.session.commit() if context_auto_commit.get() else db.session.flush()
            return self

        def delete(self):
            """Override default model's delete"""
            global context_auto_commit
            db.session.delete(self)
            db.session.commit() if context_auto_commit.get() else db.session.flush()

        def to_dict(self):
            return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

        @classmethod
        def count(cls, **attrs) -> int:
            return db.session.query(func.count(cls.id)).filter_by(**attrs).scalar()

        @classmethod
        def get_fields(cls) -> List[str]:
            return [c.name for c in cls.__table__.columns]

    return BaseModel
