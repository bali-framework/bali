import datetime
import decimal
import enum
import uuid

from bali.db import db
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.event import listens_for
from sqlalchemy.util.langhelpers import symbol

__all__ = ["FieldTracker"]


class FieldTracker(db.BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String(64), nullable=False)
    pk = Column(Integer, nullable=False)
    field = Column(String(64), nullable=False)
    old_value = Column(JSON)
    new_value = Column(JSON)

    @classmethod
    def listen_for(cls, *fields):
        for i in fields:

            @listens_for(i, "set")
            def create(target, value, oldvalue, initiator):
                if oldvalue is symbol('NO_VALUE'):
                    return value

                try:
                    db.session.add(
                        cls(
                            model=target.__tablename__,
                            pk=target.id,
                            field=initiator.key,
                            old_value=_convert(oldvalue),
                            new_value=_convert(value),
                        )
                    )
                except Exception:
                    pass
                finally:
                    return value


def _convert(value):
    if isinstance(value, datetime.datetime):
        r = value.isoformat()
        if value.microsecond:
            r = r[:23] + r[26:]
        return r
    elif isinstance(value, datetime.date):
        return value.isoformat()
    elif isinstance(value, datetime.time):
        assert value.utcoffset() is None, "aware time not allowed"
        r = value.isoformat()
        if value.microsecond:
            r = r[:12]
        return r
    elif isinstance(value, enum.Enum):
        return value.name
    elif isinstance(value, (decimal.Decimal, uuid.UUID)):
        return str(value)
    else:
        return value
