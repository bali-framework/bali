from typing import Container, Optional, Type

from fastapi.dependencies.utils import get_typed_signature
from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty

from .generic import *


class OrmConfig(BaseConfig):
    orm_mode = True


# noinspection PyDefaultArgument
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
    # noinspection PyTypeChecker
    pydantic_model = create_model(
        db_model.__name__,
        __config__=config,
        **fields  # noqa
    )
    return pydantic_model


def get_schema_in(func, default_by_action=False):
    """
    Inspects action function to get the schema

    if `default_by_action` is provided, It is generally to obtain a schema
    that can be used in a `generic action` method.
    (like: list/create/get/update/delete)
    """

    # Generic schemas bind to actions
    generic_schemas = {
        'list': ListRequest,
        'create': CreateRequest,
        'get': GetRequest,
        'update': UpdateRequest,
        'delete': DeleteRequest,
    }

    typed_signature = get_typed_signature(func)
    signature_params = typed_signature.parameters

    # 1st argument is self
    # 2st argument is schema_in
    index = 0
    for param_name, param in signature_params.items():
        index += 1
        if index == 2 or param_name == 'schema_in':
            schema_in = param.annotation
            if not schema_in:

                if default_by_action:
                    return generic_schemas.get(func.__name__)

                raise ValueError(
                    'Custom actions must provide `schema_in` argument with annotation'
                )

            return schema_in
    else:
        raise ValueError('Custom actions arguments error')
