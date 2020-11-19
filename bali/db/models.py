from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean


def get_base_model(db):
    class BaseModel(db.Model):
        __abstract__ = True

        created_time = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
        updated_time = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
        is_active = Column(Boolean(), default=True)

    return BaseModel
