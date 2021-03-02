from datetime import datetime

import pytz
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.sql.functions import func
from sqlalchemy.types import TypeDecorator

from ..utils import timezone


class AwareDateTime(TypeDecorator):
    impl = DateTime

    @property
    def python_type(self):
        return datetime

    def process_result_value(self, value: datetime, dialect):
        return timezone.make_aware(value, timezone=pytz.UTC)

    def process_bind_param(self, value: datetime, dialect):
        if timezone.is_naive(value):
            return value

        return timezone.make_naive(value, timezone=pytz.UTC)

    def process_literal_param(self, value: datetime, dialect):
        return value.isoformat()


def get_base_model(db):
    class BaseModel(db.Model):
        __abstract__ = True

        created_time = Column(AwareDateTime, default=datetime.utcnow)
        updated_time = Column(AwareDateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_active = Column(Boolean, default=True)

        def to_dict(self):
            return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

        @classmethod
        def count(cls, **attrs) -> int:
            return db.query(func.count(cls.id)).filter(*attrs).scalar()

    return BaseModel
