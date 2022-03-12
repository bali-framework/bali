from typing import Tuple

from sqlalchemy import desc, asc
from sqlalchemy.sql import operators
from sqlalchemy.sql.expression import extract

from ..exceptions import OperatorModelError

OPERATOR_SPLITTER = '__'
REVERSER = "-"

OPERATORS = {
    'isnull': lambda c, v: (c == None) if v else (c != None),  # noqa
    'exact': operators.eq,
    'ne': operators.ne,  # not equal or is not (for None)
    'gt': operators.gt,
    'gte': operators.ge,
    'lt': operators.lt,
    'lte': operators.le,
    'in': operators.in_op,
    'notin': operators.notin_op,
    'between': lambda c, v: c.between(v[0], v[1]),
    'like': operators.like_op,
    'ilike': operators.ilike_op,
    'startswith': operators.startswith_op,
    'istartswith': lambda c, v: c.ilike(v + '%'),
    'endswith': operators.endswith_op,
    'iendswith': lambda c, v: c.ilike('%' + v),
    'contains': lambda c, v: c.ilike('%{v}%'.format(v=v)),
    'year': lambda c, v: extract('year', c) == v,
    'year_ne': lambda c, v: extract('year', c) != v,
    'year_gt': lambda c, v: extract('year', c) > v,
    'year_ge': lambda c, v: extract('year', c) >= v,
    'year_lt': lambda c, v: extract('year', c) < v,
    'year_le': lambda c, v: extract('year', c) <= v,
    'month': lambda c, v: extract('month', c) == v,
    'month_ne': lambda c, v: extract('month', c) != v,
    'month_gt': lambda c, v: extract('month', c) > v,
    'month_ge': lambda c, v: extract('month', c) >= v,
    'month_lt': lambda c, v: extract('month', c) < v,
    'month_le': lambda c, v: extract('month', c) <= v,
    'day': lambda c, v: extract('day', c) == v,
    'day_ne': lambda c, v: extract('day', c) != v,
    'day_gt': lambda c, v: extract('day', c) > v,
    'day_ge': lambda c, v: extract('day', c) >= v,
    'day_lt': lambda c, v: extract('day', c) < v,
    'day_le': lambda c, v: extract('day', c) <= v,
}


def get_filters_expr(cls, **filters):
    if not callable(cls):
        raise OperatorModelError('Operator model must provide')

    expressions = []
    for attr, value in filters.items():
        if OPERATOR_SPLITTER in attr:
            attr_name, op_name = attr.rsplit(OPERATOR_SPLITTER, 1)
            if op_name not in OPERATORS:
                raise KeyError(
                    'Expression `{}` has incorrect '
                    'operator `{}`'.format(attr, op_name)
                )
            op = OPERATORS[op_name]
        else:
            attr_name, op = attr, operators.eq

        column = getattr(cls, attr_name)
        expressions.append(op(column, value))

    return expressions


def dj_lookup_to_sqla(expression: str) -> Tuple:
    col_name, op_name = expression, "exact"
    if OPERATOR_SPLITTER in col_name:
        col_name, op_name = col_name.rsplit(OPERATOR_SPLITTER, 1)
    return OPERATORS[op_name], col_name


def dj_ordering_to_sqla(expression: str):
    wrapper = desc if expression.startswith(REVERSER) else asc
    return wrapper(expression.lstrip(REVERSER))
