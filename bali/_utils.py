import re
from typing import Callable, Any

from grpc import Server
from pydantic import BaseModel


def singleton(cls):
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    def __clear__():
        _instance.clear()

    inner.__clear__ = __clear__

    return inner


ServiceAdderNamePattern = re.compile(r"^add_.*_to_server$")


def get_service_adder(module) -> Callable[[object, Server], None]:
    namespace = vars(module)
    for i in dir(module):
        if ServiceAdderNamePattern.match(i):
            return namespace[i]


def pluralize(noun):
    """pluralize a given word

    ref:
    https://www.codespeedy.com/program-that-pluralize-a-given-word-in-python/

    :param noun:
    :return:
    """
    if re.search('[sxz]$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeioudgkprt]h$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[aeiou]y$', noun):
        return re.sub('y$', 'ies', noun)
    else:
        return noun + 's'


def parse_dict(item: Any, schema: BaseModel = None):
    """Parse model instance, schema, dict to dict"""
    if isinstance(item, dict):
        return item

    # Transform model instance to schema
    if hasattr(item, '_sa_instance_state'):
        if not schema:
            raise ValueError(
                "Model instance can't parse to dict without schema"
            )
        return schema.from_orm(item).dict()

    return item.dict()
