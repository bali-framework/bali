from pydantic import BaseModel
from fastapi_pagination import paginate as default_paginate
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from .exceptions import ReturnTypeError


def paginate(sequence, params=None, is_rpc=False):
    if isinstance(sequence, BaseModel):
        raise ReturnTypeError('Paginate should return a sequence')

    # determine paginator type
    if isinstance(sequence, list):
        paginator_func = default_paginate

    else:
        paginator_func = sqlalchemy_paginate

    if params:
        paginator = paginator_func(sequence, params)
    else:
        paginator = paginator_func(sequence)

    if not is_rpc:
        return paginator

    response_data = paginator.dict()

    # convert items to dict
    items = response_data.get('items', [])
    items = [item if isinstance(item, dict) else item.dict() for item in items]

    response_data.update(
        count=response_data.get('total'),
        items=items,
        data=items,
    )

    return response_data
