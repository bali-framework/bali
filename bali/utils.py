from datetime import datetime, date
from typing import Tuple

# noinspection PyUnresolvedReferences
import dateparser
from google.protobuf import json_format
from sqlalchemy.sql import operators
from sqlalchemy.sql.expression import extract, desc, asc

# modified from https://github.com/jpsca/sqla-wrapper
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


def dj_query(expression: str) -> Tuple:
    splitter = "__"
    col_name, op_name = expression, "exact"
    if splitter in col_name:
        col_name, op_name = col_name.rsplit(splitter, 1)
    return OPERATORS[op_name], col_name


def dj_ordering(expression: str):
    reverse = "-"
    wrapper = desc if expression.startswith(reverse) else asc
    return wrapper(expression.lstrip(reverse))


class ProtobufParser(json_format._Parser):  # noqa
    def _ConvertValueMessage(self, value, message):
        """Convert a JSON representation into Value message."""
        if isinstance(value, dict):
            self._ConvertStructMessage(value, message.struct_value)
        elif isinstance(value, list):
            self._ConvertListValueMessage(value, message.list_value)
        elif isinstance(value, (datetime, date)):
            message.string_value = value.isoformat()
        elif value is None:
            message.null_value = 0
        elif isinstance(value, bool):
            message.bool_value = value
        elif isinstance(value, json_format.six.string_types):
            message.string_value = value
        elif isinstance(value, json_format._INT_OR_FLOAT):  # noqa
            message.number_value = value
        else:
            raise json_format.ParseError(
                'Value {0} has unexpected type {1}.'.format(value, type(value))
            )


class ProtobufPrinter(json_format._Printer):  # noqa
    def _FieldToJsonObject(self, field, value):
        """Converts field value according to Proto3 JSON Specification."""
        if field.cpp_type == json_format.descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
            return self._MessageToJsonObject(value)
        elif field.cpp_type == json_format.descriptor.FieldDescriptor.CPPTYPE_ENUM:
            if self.use_integers_for_enums:
                return value
            if field.enum_type.full_name == 'google.protobuf.NullValue':
                return None
            enum_value = field.enum_type.values_by_number.get(value, None)
            if enum_value is not None:
                return enum_value.name
            else:
                if field.file.syntax == 'proto3':
                    return value
                raise json_format.SerializeToJsonError(
                    'Enum field contains an integer value '
                    'which can not mapped to an enum value.'
                )
        elif field.cpp_type == json_format.descriptor.FieldDescriptor.CPPTYPE_STRING:
            if field.type == json_format.descriptor.FieldDescriptor.TYPE_BYTES:
                # Use base64 Data encoding for bytes
                return json_format.base64.b64encode(value).decode('utf-8')
            else:
                return value
        elif field.cpp_type == json_format.descriptor.FieldDescriptor.CPPTYPE_BOOL:
            return bool(value)
        elif field.cpp_type in json_format._INT64_TYPES:  # noqa
            return str(value)
        elif field.cpp_type in json_format._FLOAT_TYPES:  # noqa
            if json_format.math.isinf(value):
                if value < 0.0:
                    return json_format._NEG_INFINITY  # noqa
                else:
                    return json_format._INFINITY  # noqa
            if json_format.math.isnan(value):
                return json_format._NAN  # noqa
            if self.float_format:
                return float(format(value, self.float_format))
            else:
                converted_i = int(value)
                converted_f = float(value)
                return converted_i if converted_f == converted_i else converted_f

        return value


def MessageToDict(  # noqa
        message,
        including_default_value_fields=False,
        preserving_proto_field_name=False,
        use_integers_for_enums=False,
        descriptor_pool=None,
        float_precision=None
):
    printer = ProtobufPrinter(
        including_default_value_fields,
        preserving_proto_field_name,
        use_integers_for_enums,
        descriptor_pool,
        float_precision=float_precision
    )
    return printer._MessageToJsonObject(message)  # noqa


def ParseDict(  # noqa
        js_dict,
        message,
        ignore_unknown_fields=False,
        descriptor_pool=None
):
    parser = ProtobufParser(ignore_unknown_fields, descriptor_pool)
    parser.ConvertMessage(js_dict, message)
    return message
