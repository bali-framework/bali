from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean


def get_base_model(db):
    class BaseModel(db.Model):
        __abstract__ = True

        created_time = Column(DateTime(timezone=True), default=datetime.utcnow)
        updated_time = Column(
            DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
        )
        is_active = Column(Boolean(), default=True)

        def to_dict(self):
            return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

    return BaseModel
