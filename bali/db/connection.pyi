from datetime import datetime
from typing import Dict, Optional, Any, Type, TypeVar, Union, List, Tuple

from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Column
from sqla_wrapper import SQLAlchemy

_M = TypeVar("_M")
_DateTimeField = Union[datetime, Column[Optional[datetime]]]
_BooleanField = Union[bool, Column[Optional[bool]]]


class BaseModel:
    __abstract__ = True
    __asdict_include_hybrid_properties__ = False
    created_time: _DateTimeField
    updated_time: _DateTimeField
    is_active: _BooleanField

    def _asdict(self, **kwargs) -> Dict[str, Any]: ...

    def to_dict(self, **kwargs) -> Dict[str, Any]: ...

    def dict(self, **kwargs) -> Dict[str, Any]: ...

    @classmethod
    def exists(cls: Type[_M], **attrs) -> bool: ...

    @classmethod
    def create(cls: Type[_M], **attrs) -> _M: ...

    @classmethod
    def create_or_first(cls: Type[_M], **attrs) -> _M: ...

    @classmethod
    def first(cls: Type[_M], **attrs) -> Optional[_M]: ...

    @classmethod
    def first_or_error(cls: Type[_M], **attrs) -> _M:
        """
        raise: ValueError
        """
        ...

    @classmethod
    def query(cls: Type[_M]) -> Query: ...

    def save(self) -> _M: ...

    def delete(self) -> None: ...

    @classmethod
    def count(cls: Type[_M], **attrs) -> int: ...

    @classmethod
    def get_fields(cls: Type[_M]) -> List[str]: ...

    @classmethod
    def get_or_create(cls: Type[_M], defaults: Dict[str, Any], **attrs) -> Tuple[_M, bool]: ...

    @classmethod
    def update_or_create(cls: Type[_M], defaults: Dict[str, Any], **attrs) -> Tuple[_M, bool]: ...


class DB(SQLAlchemy):
    BaseModel: BaseModel

    _async_engine: Any

    def connect(self, database_uri: str) -> None: ...

    @property
    def session(self) -> Session: ...

    def transaction(self) -> None: ...

    async def async_session(self) -> Any: ...


db = DB()
