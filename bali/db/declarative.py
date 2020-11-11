from typing import Any
from sqla_wrapper import SQLAlchemy

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from .connection import db

db._session = SQLAlchemy()


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


# Next enhanced declarative base by SQLA-wrapper
NextBase = db.Model
