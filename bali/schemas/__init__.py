from typing import Container, Optional, Type

from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty

from .generic import *


class OrmConfig(BaseConfig):
    orm_mode = True


def model_to_schema(
    db_model: Type,
    *,
    config: Type = OrmConfig,
    exclude: Container[str] = [],
    partial=False  # noqa
) -> Type[BaseModel]:
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                python_type: Optional[type] = None
                if hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"

                default = None
                if column.default is None and not column.nullable:
                    default = ...

                if partial:
                    fields[name] = (Optional[python_type], None)
                else:
                    fields[name] = (python_type, default)
    pydantic_model = create_model(
        db_model.__name__,
        __config__=config,
        **fields  # noqa
    )
    return pydantic_model
